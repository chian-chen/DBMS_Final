
/*
https://dev.mysql.com/doc/extending-mysql/8.0/en/adding-loadable-function.html
*/
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h> // read(), write(), close()
#include <mysql.h>
// #include "clip_api.h"
#include <stdio.h>
// Call xxx_init() to let the aggregate function allocate any memory it needs for storing results.
// The initialization function for xxx().
bool clip_init(UDF_INIT *initid, UDF_ARGS *args, char *message)
{
    return 0;
}

/* The deinitialization function for xxx(). If present, it should deallocate any memory allocated by the initialization function.
 */

void clip_deinit(UDF_INIT *initid)
{
}
int send_path(int sockfd, char* path)
{
    char buff[12] = {'\0'};
    int n;
    write(sockfd, path, strlen(path) + 1);
    read(sockfd, buff, sizeof(buff));
    return atoi(buff);
}

long long clip(UDF_INIT *initid, UDF_ARGS *args,
              char *is_null, char *error){
    int sockfd, connfd;
    struct sockaddr_in servaddr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("socket creation failed...\n");
        exit(0);
    }
    else
        printf("Socket successfully created..\n");
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    servaddr.sin_port = htons(9999);
    if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr))
        != 0) {
        printf("connection with the server failed...\n");
        exit(0);
    }
    else
        printf("connected to the server..\n");
    int result = send_path(sockfd, "path:/mysqludf/img.png");
    return result;
}
