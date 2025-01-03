Explain the following code in detail:
```c
#include <libproc.h>         /* for umask() */
#include <stdio.h>           /* for perror(), fprintf(), dprintf(), stderr */
#include <stdlib.h>          /* for malloc(), exit() and statuses*/
#include <sys/fcntl.h>       /* for open() */
#include <arpa/inet.h>       /* for inet_ntop() */
#include <netinet/tcp_var.h> /* for CTL_NET, TCPCTL_PCBLIST */
#include <netinet/udp_var.h> /* for UDPCTL_PCBLIST*/
#include <getopt.h>
#include <sys/socketvar.h>

#include "config.h"

const char *tcpstates[] = {
	"CLOSED", "LISTEN", "SYN_SENT", "SYN_RECEIVED",
	"ESTABLISHED", "CLOSE_WAIT", "FIN_WAIT_1", "CLOSING",
	"LAST_ACK", "FIN_WAIT_2", "TIME_WAIT", "UNKNOWN"
};

void parse_arguments(int argc, char **argv, int *interval, char **pipe_path);
void daemonize();
void signal_handler(int sig);
void process_mib(int *mib, int pipe_fd);
void print_tcp_socket(int fd, struct inpcb *inp, int state);
void print_udp_socket(int fd, struct inpcb *inp);
void convert_addresses(struct inpcb *inp, char *local_addr, char *remote_addr);

int main(int argc, char *argv[]) {
	int interval = DEFAULT_INTERVAL;
	char *pipe_path = DEFAULT_PIPE_PATH;

	parse_arguments(argc, argv, &interval, &pipe_path);

	daemonize();
	signal(SIGTERM, signal_handler); signal(SIGINT, signal_handler);

	int pipe_fd = open(pipe_path, O_WRONLY);
	if (pipe_fd == -1) {
		perror("open pipe"); exit(EXIT_FAILURE);
	}
	while (1) {
		int udp_mib[] = { CTL_NET, PF_INET, IPPROTO_UDP, UDPCTL_PCBLIST };
		process_mib(udp_mib, pipe_fd);
		int tcp_mib[] = { CTL_NET, PF_INET, IPPROTO_TCP, TCPCTL_PCBLIST };
		process_mib(tcp_mib, pipe_fd);
		usleep(interval);
	}
	close(pipe_fd);
	return 0;
}

void parse_arguments(int argc, char *argv[], int *interval, char **pipe_path) {
	int opt;
	struct option long_options[] = {
		{"interval", optional_argument, 0, 'i'},
		{"pipe_path", optional_argument, 0, 'p'},
		{0, 0, 0, 0}
	};
	while ((opt = getopt_long(argc, argv, "i:p:", long_options, NULL)) != -1) {
		switch (opt) {
			case 'i': *interval = atoi(optarg); break;
			case 'p': *pipe_path = optarg; break;
			default: fprintf(stderr,
					"Usage: %s [-i interval] [-p pipe_path]\n",
					argv[0]); exit(EXIT_FAILURE);
		}
	}
}

void daemonize() {
	pid_t pid, sid;
	pid = fork();
	if (pid < 0) exit(EXIT_FAILURE);
	if (pid > 0) exit(EXIT_SUCCESS);
	umask(0);
	sid = setsid();
	if (sid < 0) exit(EXIT_FAILURE);
	if ((chdir("/")) < 0) exit(EXIT_FAILURE);
	close(STDIN_FILENO); close(STDOUT_FILENO); close(STDERR_FILENO);
}

void signal_handler(int sig) { exit(0); }

void process_mib(int mib[], int pipe_fd){
	size_t size_of_buf;
	if (sysctl(mib, 4, NULL, &size_of_buf, NULL, 0) < 0) {
		perror("sysctl: size retrieval"); exit(EXIT_FAILURE);
	}
	/* Allocate memory to hold the data */
	char *buf = malloc(size_of_buf); if (buf == NULL) {
		perror("malloc"); exit(EXIT_FAILURE);
	}
	/* Get the actual data to allocated buf */
	if (sysctl(mib, 4, buf, &size_of_buf, NULL, 0) < 0) {
		perror("sysctl: data retrieval");
		free(buf); exit(EXIT_FAILURE);
	}
	struct xinpgen *xig;
	xig = (struct xinpgen *)buf;
	xig = (struct xinpgen *)((char *)xig + xig->xig_len);
	if (mib[2] == 6) { /* 6 defined as IPPROTO_TCP in MIB */
		while (xig->xig_len > sizeof(struct xinpgen)) {
			struct xtcpcb *tp = (struct xtcpcb *)xig;
			struct tcpcb *tcp = &tp->xt_tp;
			struct inpcb *inp = &tp->xt_inp;
			int state = tcp->t_state;
			print_tcp_socket(pipe_fd, inp, state);
			xig = (struct xinpgen *)((char *)xig + xig->xig_len);
		} 
	} else if (mib[2] == 17 ) { /* 17 defined as IPPROTO_UDP in MIB */
		while (xig->xig_len > sizeof(struct xinpgen)) {
			struct xtcpcb *tp = (struct xtcpcb *)xig;
			struct inpcb *inp = &tp->xt_inp;
			print_udp_socket(pipe_fd, inp);
			xig = (struct xinpgen *)((char *)xig + xig->xig_len);
		}
	}
	free(buf);
	write(pipe_fd, "\n", sizeof(char));
}

void print_tcp_socket(int fd, struct inpcb *inp, int state) {
	char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];
	convert_addresses(inp, local_addr, remote_addr);
	const char *state_string = (state >= 0 && state < sizeof(tcpstates) / sizeof(tcpstates[0]))
		? tcpstates[state] : tcpstates[11];
	dprintf(fd, "TCP,%s:%d,%s:%d,%s\t",
		   local_addr,  ntohs(inp->inp_lport),
		   remote_addr, ntohs(inp->inp_fport),
		   state_string
	);
}

void print_udp_socket(int fd, struct inpcb *inp) {
	char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];
	convert_addresses(inp, local_addr, remote_addr);
	dprintf(fd, "UDP,%s:%d,%s:%d\t",
		   local_addr,  ntohs(inp->inp_lport),
		   remote_addr, ntohs(inp->inp_fport)
	);
}

void convert_addresses(struct inpcb *inp, char *local_addr, char *remote_addr) {
	if (inp->inp_vflag & INP_IPV4) {
		inet_ntop(AF_INET, &inp->inp_laddr.s_addr, local_addr, INET6_ADDRSTRLEN);
		inet_ntop(AF_INET, &inp->inp_faddr.s_addr, remote_addr, INET6_ADDRSTRLEN);
	} else if (inp->inp_vflag & INP_IPV6) {
		inet_ntop(AF_INET6, &inp->in6p_laddr, local_addr, INET6_ADDRSTRLEN);
		inet_ntop(AF_INET6, &inp->in6p_faddr, remote_addr, INET6_ADDRSTRLEN);
	}
}
```