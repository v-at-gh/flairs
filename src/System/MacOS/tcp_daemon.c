#include <libproc.h>
#include <stdio.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/sysctl.h>
#include <sys/fcntl.h>
#include <unistd.h>
#include <sys/socketvar.h>

#include <netinet/tcp_var.h>
#include <netinet/tcp_fsm.h> // tcp states

#define DEFAULT_INTERVAL  1000000
#define DEFAULT_PIPE_PATH "/tmp/tcp_connections.pipe"

const char *tcpstates[] = {
    "CLOSED", "LISTEN", "SYN_SENT", "SYN_RECEIVED",
    "ESTABLISHED", "CLOSE_WAIT", "FIN_WAIT_1", "CLOSING",
    "LAST_ACK", "FIN_WAIT_2", "TIME_WAIT", "UNKNOWN"
};

void daemonize() {
    pid_t pid, sid;
    pid = fork();
    if (pid < 0) { exit(EXIT_FAILURE); }
    if (pid > 0) { exit(EXIT_SUCCESS); }
    umask(0);
    sid = setsid();
    if (sid < 0) { exit(EXIT_FAILURE); }
    if ((chdir("/")) < 0) { exit(EXIT_FAILURE); }
    close(STDIN_FILENO); close(STDOUT_FILENO); close(STDERR_FILENO);
}

void signal_handler(int sig) { exit(0); }

void print_tcp_socket(int fd, struct inpcb *inp, int state) {
    char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];

    if (inp->inp_vflag & INP_IPV4) {
        inet_ntop(AF_INET, &inp->inp_laddr.s_addr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET, &inp->inp_faddr.s_addr, remote_addr, sizeof(remote_addr));
    } else if (inp->inp_vflag & INP_IPV6) {
        inet_ntop(AF_INET6, &inp->in6p_laddr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET6, &inp->in6p_faddr, remote_addr, sizeof(remote_addr));
    }

    const char *state_string = (state >= 0 && state < sizeof(tcpstates) / sizeof(tcpstates[0])) ? tcpstates[state] : tcpstates[11];

    dprintf(fd, "%s:%d,%s:%d,%s\t",
           local_addr,  ntohs(inp->inp_lport),
           remote_addr, ntohs(inp->inp_fport),
           state_string
           );
}

int main(int argc, char *argv[]) {
    // TODO: move arg parsing to a new function
    int interval = DEFAULT_INTERVAL;
    char *pipe_path = DEFAULT_PIPE_PATH;

    int opt;
    while ((opt = getopt(argc, argv, "i:p:")) != -1) {
        switch (opt) {
        case 'i': interval = atoi(optarg); break;
        // TODO fix pipe path parsing
        case 'p': pipe_path = optarg; break;
        default:
            fprintf(stderr, "Usage: %s [-i interval] [-p pipe_path]\n", argv[0]);
            exit(EXIT_FAILURE);
        }
    }

    daemonize();
    signal(SIGTERM, signal_handler); signal(SIGINT, signal_handler);

    int pipe_fd = open(pipe_path, O_WRONLY);
    if (pipe_fd == -1) {
        perror("open pipe"); exit(EXIT_FAILURE);
    }

    while (1) {
        int mib[] = { CTL_NET, PF_INET, IPPROTO_TCP, TCPCTL_PCBLIST };
        size_t len;
        // Test getting the size of the data
        if (sysctl(mib, 4, NULL, &len, NULL, 0) < 0) {
            perror("sysctl: size retrieval"); exit(EXIT_FAILURE);
        }
        // Allocate memory to hold the data
        char *buf = malloc(len); if (buf == NULL) {
            perror("malloc"); exit(EXIT_FAILURE);
        }
        // Get the actual data to allocated buf
        if (sysctl(mib, 4, buf, &len, NULL, 0) < 0) {
            perror("sysctl: data retrieval");
            free(buf); exit(EXIT_FAILURE);
        }
        struct xinpgen *xig, *oxig;
        xig = oxig = (struct xinpgen *)buf;
        xig = (struct xinpgen *)((char *)xig + xig->xig_len);

        while (xig->xig_len > sizeof(struct xinpgen)) {
            struct xtcpcb *tp = (struct xtcpcb *)xig;
            struct tcpcb *tcp = &tp->xt_tp;
            int state = tcp->t_state;
            struct inpcb *inp = &tp->xt_inp;
            struct xsocket *so = &tp->xt_socket;
            print_tcp_socket(pipe_fd, inp, state);
            xig = (struct xinpgen *)((char *)xig + xig->xig_len);
        }
        // Print new-line terminator
        dprintf(pipe_fd, "\n");
        free(buf);
        usleep(interval);
    }

    close(pipe_fd);
    return 0;
}

