
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
#include <ctype.h>

// Function to check if the string contains ".png"
int contains_image_extension(const char *str) {
    const char *extensions[] = { ".png", ".jpeg" };
    size_t num_extensions = sizeof(extensions) / sizeof(extensions[0]);

    // Convert the input string to lower case
    char lower_str[256];
    strncpy(lower_str, str, sizeof(lower_str) - 1);
    lower_str[sizeof(lower_str) - 1] = '\0';
    for (char *p = lower_str; *p; ++p) {
        *p = tolower((unsigned char)*p);
    }

    // Check for each extension
    for (size_t i = 0; i < num_extensions; ++i) {
        if (strstr(lower_str, extensions[i]) != NULL) {
            return 1; // Extension found
        }
    }

    return 0; // No extensions found
}


// Call xxx_init() to let the aggregate function allocate any memory it needs for storing results.
// The initialization function for xxx().
bool image_sim_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    // if (args->arg_count != 2) {
    //     strcpy(message, "load_image() requires exactly two arguments: column_value and image_path");
    //     return 1;
    // }

    if (args->arg_type[0] != STRING_RESULT || args->arg_type[1] != STRING_RESULT) {
        strcpy(message, "load_image() requires both arguments to be strings");
        return 1;
    }

    return 0;
}

/* The deinitialization function for xxx(). If present, it should deallocate any memory allocated by the initialization function.
 */

// Deinitialization function for the UDF
void image_sim_deinit(UDF_INIT *initid) {
    // Nothing to clean up
}

int send_path(int sockfd, char* path)
{
    char buff[12] = {'\0'};
    int n;
    write(sockfd, path, strlen(path) + 1);
    read(sockfd, buff, sizeof(buff));
    return atoi(buff);
}

// The UDF itself
double image_sim(UDF_INIT *initid, UDF_ARGS *args, char *result, unsigned long *length, char *is_null, char *error) {
    const char *column_value = args->args[0];
    const char *image_path = args->args[1];

    // Determine if image_path contains ".png"
    const char *prefix = "sim:";
    const char *sim_str = "sim_str:";
    // const char *result_prefix = contains_png(image_path) ? prefix : sim_str;

    const char *result_prefix;

    if (args->arg_count == 3) {
        if(strcmp(args->args[2],"PSNR") == 0){
            result_prefix = "sim_psnr:";
        }
        else if (strcmp(args->args[2],"SSIM") == 0){
            result_prefix = "sim_ssim:";
        }
        else if (strcmp(args->args[2],"LPIPS") == 0){
            result_prefix = "sim_lpips:";
        }
        else{
            result_prefix = "sim:";
        }
    }
    else{
        result_prefix = contains_image_extension(image_path) ? prefix : sim_str;
    }

    // Calculate the length of the concatenated string
    size_t len_column_value = strlen(column_value);
    size_t len_image_path = strlen(image_path);
    size_t len_result = strlen(result_prefix) + len_column_value + len_image_path + 2; // +2 for '_' and '\0'

    // Allocate memory for the concatenated string
    char *result_str = (char *)malloc(len_result);
    if (result_str == NULL) {
        perror("Error allocating memory");
        exit(0);
    }

    // Concatenate the strings with an underscore in the middle
    strcpy(result_str, result_prefix);
    strcat(result_str, column_value);
    strcat(result_str, "$");
    strcat(result_str, image_path);

    // Socket
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
    // return 0.88;

    int similarity = send_path(sockfd, result_str);
    // int similarity = send_path(sockfd, "sim:/mysqludf/img.png_/mysqludf/img.png");
    double convertResult;
    convertResult = (double)similarity / 100;
    return convertResult;

}

// double image_sim(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error) {
//     const char *column_value = args->args[0];
//     const char *image_path = args->args[1];

//     // Calculate the length of the concatenated string
//     unsigned long column_length = args->lengths[0];
//     unsigned long path_length = args->lengths[1];
//     unsigned long total_length = column_length + path_length;

//     return (double)total_length;
// }

// long long clip(UDF_INIT *initid, UDF_ARGS *args,
//               char *is_null, char *error){
//     int sockfd, connfd;
//     struct sockaddr_in servaddr;

//     sockfd = socket(AF_INET, SOCK_STREAM, 0);
//     if (sockfd == -1) {
//         printf("socket creation failed...\n");
//         exit(0);
//     }
//     else
//         printf("Socket successfully created..\n");
//     servaddr.sin_family = AF_INET;
//     servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
//     servaddr.sin_port = htons(9999);
//     if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr))
//         != 0) {
//         printf("connection with the server failed...\n");
//         exit(0);
//     }
//     else
//         printf("connected to the server..\n");
//     int result = send_path(sockfd, "path:/mysqludf/img.png");
//     return result;
// }