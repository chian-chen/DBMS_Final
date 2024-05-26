PY_CFLAGS  := $(shell python3-config --cflags)
PY_LDFLAGS := $(shell python3-config --embed --ldflags)

all:
	gcc $(PY_CFLAGS) -fPIE -c api.c -o api.o
	gcc api.o $(PY_LDFLAGS) -o api
share:
	gcc $(PY_CFLAGS) -fPIE -fPIC -c api.c -o api.o
	gcc api.o -shared $(PY_LDFLAGS) -o api.so