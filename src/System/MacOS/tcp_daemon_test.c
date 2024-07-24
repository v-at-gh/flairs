#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <netinet/tcp_var.h>
#include <netinet/tcp_fsm.h> // tcp states
#include <netinet/in_pcb.h>

// Define the TCP states
const char *tcpstates[] = {
    "CLOSED", "LISTEN", "SYN_SENT", "SYN_RECEIVED", "ESTABLISHED",
    "CLOSE_WAIT", "FIN_WAIT_1", "CLOSING", "LAST_ACK", "FIN_WAIT_2", "TIME_WAIT"
};

void print_tcp_socket(int fd, struct inpcb *inp, int t_flags) {
    char local_addr[INET6_ADDRSTRLEN], remote_addr[INET6_ADDRSTRLEN];
    const char *state = (t_flags >= 0 && t_flags < 11) ? tcpstates[t_flags] : "UNKNOWN";

    if (inp->inp_vflag & INP_IPV4) {
        inet_ntop(AF_INET, &inp->inp_laddr.s_addr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET, &inp->inp_faddr.s_addr, remote_addr, sizeof(remote_addr));
    } else if (inp->inp_vflag & INP_IPV6) {
        inet_ntop(AF_INET6, &inp->in6p_laddr, local_addr, sizeof(local_addr));
        inet_ntop(AF_INET6, &inp->in6p_faddr, remote_addr, sizeof(remote_addr));
    }

    dprintf(fd, "%s:%d,%s:%d,%s\t",
            local_addr, ntohs(inp->inp_lport),
            remote_addr, ntohs(inp->inp_fport),
            state);
}

// Definitions for the TCP state values
#define TCPS_CLOSED      0
#define TCPS_LISTEN      1
#define TCPS_SYN_SENT    2
#define TCPS_SYN_RECEIVED 3
#define TCPS_ESTABLISHED 4
#define TCPS_CLOSE_WAIT  5
#define TCPS_FIN_WAIT_1  6
#define TCPS_CLOSING     7
#define TCPS_LAST_ACK    8
#define TCPS_FIN_WAIT_2  9
#define TCPS_TIME_WAIT   10

// Definition of the inpcb structure and INP_IPV4/INP_IPV6 flags should be included as per your system requirements
struct inpcb {
    int inp_vflag;
    struct in_addr inp_laddr;
    struct in_addr inp_faddr;
    struct in6_addr in6p_laddr;
    struct in6_addr in6p_faddr;
    uint16_t inp_lport;
    uint16_t inp_fport;
};

#define INP_IPV4 0x1
#define INP_IPV6 0x2

int main() {
    // Example usage (assuming appropriate initialization of the inpcb structure and file descriptor)
    struct inpcb example_inpcb = {
        .inp_vflag = INP_IPV4,
        .inp_laddr = { .s_addr = inet_addr("192.168.0.1") },
        .inp_faddr = { .s_addr = inet_addr("192.168.0.2") },
        .inp_lport = htons(12345),
        .inp_fport = htons(80)
    };

    int example_fd = 1; // Standard output
    int example_state = TCPS_ESTABLISHED;

    print_tcp_socket(example_fd, &example_inpcb, example_state);

    return 0;
}
