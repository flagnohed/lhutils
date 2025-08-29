CFLAGS = -g -O2
CFLAGS += -D_POSIX_C_SOURCE=200809L
CFLAGS += -std=c99 -Wpedantic -pedantic-errors
# CFLAGS += -Werror
CFLAGS += -Wall
CFLAGS += -Wextra
CFLAGS += -Waggregate-return
CFLAGS += -Wbad-function-cast
CFLAGS += -Wcast-align
CFLAGS += -Wcast-qual
CFLAGS += -Wdeclaration-after-statement
CFLAGS += -Wfloat-equal
CFLAGS += -Wformat=2
CFLAGS += -Wlogical-op
CFLAGS += -Wmissing-declarations
CFLAGS += -Wmissing-include-dirs
CFLAGS += -Wmissing-prototypes
CFLAGS += -Wnested-externs
CFLAGS += -Wpointer-arith
CFLAGS += -Wredundant-decls
CFLAGS += -Wsequence-point
CFLAGS += -Wshadow
CFLAGS += -Wstrict-prototypes
CFLAGS += -Wswitch
CFLAGS += -Wundef
CFLAGS += -Wunreachable-code
CFLAGS += -Wunused-but-set-parameter
CFLAGS += -Wwrite-strings
CC = gcc
OBJS = build/main.o build/parser.o build/player.o build/test.o
lhutils: $(OBJS)
	$(CC) -o lhutils $(OBJS)

build/%.o: %.c
	$(CC) -c -o $@ $^ $(CFLAGS)

clean:
	rm -f build/*
	rm -f lhutils