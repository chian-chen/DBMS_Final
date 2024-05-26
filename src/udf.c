
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
    if (args->arg_count != 1 || args->arg_type[0] != STRING_RESULT) {
        strcpy(message, "clip() requires one string argument");
        return 1;
    }
    initid->maybe_null = 1;
    initid->max_length = 256; 
    return 0;
}

/* The deinitialization function for xxx(). If present, it should deallocate any memory allocated by the initialization function.
 */

void clip_deinit(UDF_INIT *initid)
{
}
char *clip(UDF_INIT *initid, UDF_ARGS *args,
          char *result, unsigned long *length,
          char *is_null, char *error){
    int sockfd;
    struct sockaddr_in servaddr;

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        strcpy(error, "socket creation failed");
        return NULL;
    }

    // Set server address
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    servaddr.sin_port = htons(9999);

    // Connect to server
    if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) != 0) {
        close(sockfd);
        strcpy(error, "connection with the server failed");
        return NULL;
    }

    // Prepare command
    char cmd[100] = "path:";
    strcat(cmd, args->args[0]);

    // Send command to server
    if (write(sockfd, cmd, strlen(cmd) + 1) == -1) {
        close(sockfd);
        strcpy(error, "failed to send data to server");
        return NULL;
    }

    // Read response from server
    char buff[256];
    int n = read(sockfd, buff, sizeof(buff) - 1);
    if (n == -1) {
        close(sockfd);
        strcpy(error, "failed to read data from server");
        return NULL;
    }
    buff[n] = '\0';

    // Close socket
    close(sockfd);

    // Copy response to result
    *length = strlen(buff);
    if (*length > initid->max_length) {
        *length = initid->max_length; // 限制最大长度
    }
    result = (char *)malloc(*length + 1);
    if (result == NULL) {
        strcpy(error, "memory allocation failed");
        return NULL;
    }
    strcpy(result, buff);

    return result;
}
