#include <mysql.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 函數的初始化
bool log_udf_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    // 檢查參數數量是否正確
    if (args->arg_count != 1) {
        strcpy(message, "LOG_UDF() requires one argument");
        return 1;
    }
    // 檢查參數類型是否為整數
    if (args->arg_type[0] != INT_RESULT) {
        strcpy(message, "LOG_UDF() requires an integer argument");
        return 1;
    }
    return 0;
}

// 釋放資源
void log_udf_deinit(UDF_INIT *initid) {
}

// 主計算函數
double log_udf(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error) {
    long long input = *((long long*)args->args[0]);
    if (input <= 0) {
        *is_null = 1;
        return 0.0;
    }
    return log((double)input);
}