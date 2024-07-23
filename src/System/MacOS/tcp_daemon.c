#include <libproc.h>
#include <stdio.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <netinet/tcp_var.h>
#include <sys/sysctl.h>
#include <sys/fcntl.h>
#include <unistd.h>
#include <sys/socketvar.h>

#define DEFAULT_INTERVAL 1
#define DEFAULT_PIPE_PATH "/tmp/tcp_connections.pipe"

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

const char *tcpstates[] = {
    "CLOSED", "LISTEN", "SYN_SENT", "SYN_RECEIVED", "ESTABLISHED",
    "CLOSE_WAIT", "FIN_WAIT_1", "CLOSING", "LAST_ACK", "FIN_WAIT_2", "TIME_WAIT"
};

void print_tcp_socket(int fd, struct inpcb *inp, int t_flags) {
// void print_tcp_socket(int fd, struct inpcb *inp) {
    char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];
    const char *state = (t_flags >= 0 && t_flags < 11) ? tcpstates[t_flags] : "UNKNOWN";

    if (inp->inp_vflag & INP_IPV4) {
        inet_ntop(AF_INET, &inp->inp_laddr.s_addr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET, &inp->inp_faddr.s_addr, remote_addr, sizeof(remote_addr));
    } else if (inp->inp_vflag & INP_IPV6) {
        inet_ntop(AF_INET6, &inp->in6p_laddr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET6, &inp->in6p_faddr, remote_addr, sizeof(remote_addr));
    }

    // dprintf(fd, "%s:%d,%s:%d,%s\t",
    dprintf(fd, "%s:%d,%s:%d,%s\t",
           local_addr,  ntohs(inp->inp_lport),
        //    remote_addr, ntohs(inp->inp_fport)
           remote_addr, ntohs(inp->inp_fport),
        //    );
           state);
}

int main(int argc, char *argv[]) {
    int interval = DEFAULT_INTERVAL;
    char *pipe_path = DEFAULT_PIPE_PATH;

    int opt;
    while ((opt = getopt(argc, argv, "i:p:")) != -1) {
        switch (opt) {
        case 'i':
            interval = atoi(optarg);
            break;
        case 'p':
            pipe_path = optarg;
            break;
        default:
            fprintf(stderr, "Usage: %s [-i interval] [-p pipe_path]\n", argv[0]);
            exit(EXIT_FAILURE);
        }
    }

    daemonize();
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);

    int pipe_fd = open(pipe_path, O_WRONLY);
    if (pipe_fd == -1) {
        perror("open pipe");
        exit(EXIT_FAILURE);
    }

    while (1) {
        size_t len;

        int mib[] = { CTL_NET, PF_INET, IPPROTO_TCP, TCPCTL_PCBLIST };
        if (sysctl(mib, 4, NULL, &len, NULL, 0) == -1) {
            perror("sysctl");
            exit(1);
        }

        void *buf = malloc(len);
        if (!buf) {
            perror("malloc");
            exit(1);
        }

        if (sysctl(mib, 4, buf, &len, NULL, 0) == -1) {
            perror("sysctl");
            free(buf);
            exit(1);
        }

        struct xinpgen *xig, *oxig;
        xig = oxig = (struct xinpgen *)buf;
        xig = (struct xinpgen *)((char *)xig + xig->xig_len);
        while (xig->xig_len > sizeof(struct xinpgen)) {
            struct xtcpcb *tp = (struct xtcpcb *)xig;
            struct tcpcb *tp_n = (struct tcpcb *)xig;
            struct inpcb *inp = &tp->xt_inp;
            struct xsocket *so = &tp->xt_socket;
            print_tcp_socket(pipe_fd, inp, tp_n->t_state);
            // print_tcp_socket(pipe_fd, inp);
            xig = (struct xinpgen *)((char *)xig + xig->xig_len);
        }
        dprintf(pipe_fd, "\n");
        free(buf);
        sleep(interval);
    }

    close(pipe_fd);
    return 0;
}
