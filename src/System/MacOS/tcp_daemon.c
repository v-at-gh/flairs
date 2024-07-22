#include <libproc.h>
#include <stdio.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <netinet/tcp_var.h>
#include <sys/sysctl.h>
#include <sys/fcntl.h>
#include <unistd.h>

void print_tcp_socket(int fd, struct inpcb *inp) {
    char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];
    if (inp->inp_vflag & INP_IPV4) {
        inet_ntop(AF_INET, &inp->inp_laddr.s_addr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET, &inp->inp_faddr.s_addr, remote_addr, sizeof(remote_addr));
    } else if (inp->inp_vflag & INP_IPV6) {
        inet_ntop(AF_INET6, &inp->in6p_laddr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET6, &inp->in6p_faddr, remote_addr, sizeof(remote_addr));
    }
    dprintf(fd, "%s:%d,%s:%d\t",
           local_addr, ntohs(inp->inp_lport), remote_addr, ntohs(inp->inp_fport));
}

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

int main() {
    daemonize();
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);
    int pipe_fd = open("/tmp/tcp_connections.pipe", O_WRONLY);
    if (pipe_fd == -1) { exit(1); };
    while (1) {
        size_t len;
        int mib[] = { CTL_NET, PF_INET, IPPROTO_TCP, TCPCTL_PCBLIST };
        if (sysctl(mib, 4, NULL, &len, NULL, 0) == -1) {
            perror("sysctl"); exit(1);
        }
        void *buf = malloc(len);
        if (!buf) {
            perror("malloc"); exit(1);
        };
        if (sysctl(mib, 4, buf, &len, NULL, 0) == -1) {
            perror("sysctl"); free(buf); exit(1);
        }
        struct xinpgen *xig, *oxig;
        xig = oxig = (struct xinpgen *)buf;
        xig = (struct xinpgen *)((char *)xig + xig->xig_len);
        while (xig->xig_len > sizeof(struct xinpgen)) {
            struct xtcpcb *tp = (struct xtcpcb *)xig;
            struct inpcb *inp = &tp->xt_inp;
            struct xsocket *so = &tp->xt_socket;
            print_tcp_socket(pipe_fd, inp);
            xig = (struct xinpgen *)((char *)xig + xig->xig_len);
        }
        dprintf(pipe_fd, "\n");
        free(buf); sleep(1);
    }
    close(pipe_fd);
    return 0;
}
