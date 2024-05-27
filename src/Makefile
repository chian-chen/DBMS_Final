PY_CFLAGS  := $(shell python3-config --cflags)
PY_LDFLAGS := $(shell python3-config --embed --ldflags)

all:
	gcc $(PY_CFLAGS) -fPIE -c api.c -o api.o
	gcc api.o $(PY_LDFLAGS) -o api
share:
	# gcc $(PY_CFLAGS) -rdynamic -I/usr/include/mysql -fPIE -fPIC -c udf.c  -o udf.o 
	# gcc $(PY_CFLAGS) -rdynamic -I/usr/include/mysql -fPIE -fPIC -c clip_api.c -o clip_api.o
	# gcc clip_api.o udf.o -shared $(PY_CFLAGS) $(PY_LDFLAGS) -rdynamic -o clip_api.so 
	gcc udf.c -I/usr/include/mysql -shared -o clip_api.so
	gcc udf_sim.c -I/usr/include/mysql -shared -o sim_api.so


clean: 
	rm *.so *.o *.out