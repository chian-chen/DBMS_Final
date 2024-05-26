
/*
https://dev.mysql.com/doc/extending-mysql/8.0/en/adding-loadable-function.html
*/

#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>
#include <mysql.h>

struct image_data {
    char **path;
    double **result;
}

// Call xxx_init() to let the aggregate function allocate any memory it needs for storing results.
// The initialization function for xxx().
bool clip_init(UDF_INIT *initid, UDF_ARGS *args, char *message)
{
    struct big_average_data *data;

    if (args->arg_count != 1)
    {
        strcpy(message, "wrong number of arguments: big_average() requires a column name as arguments");
        return 1;
    }

    if (!(data = new (std::nothrow) big_average_data))
    {
        stpcpy(message, "Couldn't allocate memory");
        return 1;
    }

    mpz_init(data->total);
    mpz_init(data->count);

    mpz_set_ui(data->total, 0);
    mpz_set_ui(data->count, 0);

    initid->ptr = (char *)data;
    return 0;
}

/* The deinitialization function for xxx(). If present, it should deallocate any memory allocated by the initialization function.
 */

void clip_deinit(UDF_INIT *initid)
{
    void *void_ptr = initid->ptr;
    big_average_data *data = static_cast<big_average_data *>(void_ptr);
    mpz_clear(data->total);
    mpz_clear(data->count);
    delete data;
}

/* This is only for MySQL 4.0 compability */
void big_average_reset(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *message)
{
    big_average_clear(initid, is_null, message);
    big_average_add(initid, args, is_null, message);
}

/*
This is needed to get things to work in MySQL 4.1.1 and above.
Reset the current aggregate value but do not insert the argument as the initial aggregate value for a new group.
*/
void big_average_clear(UDF_INIT *initid, char *is_null,
                       char *message)
{
    struct big_average_data *data = (struct big_average_data *)initid->ptr;
}

// Add the argument to the current aggregate value.
void big_average_add(UDF_INIT *initid, UDF_ARGS *args,
                     char *is_null,
                     char *message)
{
    if (args->args[0] && args->args[0])
    {
        struct big_average_data *data = (struct big_average_data *)initid->ptr;

        mpz_t a;
        mpz_init(a);
        const char *as = (const char *)args->args[0];
        mpz_set_str(a, as, 16);
        mpz_add(data->total, data->total, a);
        mpz_add_ui(data->count, data->count, 1);
        mpz_clear(a);
    }
}

// Call xxx() to get the result for the aggregate when the group changes or after the last row has been processed.
char *big_average(UDF_INIT *initid, UDF_ARGS *args, char *result, unsigned long *length, char *is_null, char *error)
{
    struct big_average_data *data = (struct big_average_data *)initid->ptr;
    *is_null = 0;
    // calculate the average here
    mpz_div(data->total, data->total, data->count);
    // convert total to hex string
    mpz_get_str(result, 16, data->total);
    *length = strlen(result);
    return result;
}