#include <stdio.h>
#include <string.h>
#include "test.h"

static int run_tests(void) {
    if (test_get_trainings_left()) return 1;
    if (test_print_value_predictions()) return 1;  /* Manual inspection. */
    if (test_parse_transfer_list()) return 1;
    printf("All tests passed.\n");
    return 0;
}

static void print_usage(void) {
    printf("--- lhutils ---\n");
    printf("Usage: ./lhutils [OPTION]\n");
    printf("[OPTION]:\n");
    printf("-t, --test\n");
    printf("\tRun all unit tests.\n");
}

int main(int argc, char **argv) {
    /* Parse arguments. */
    if (argc == 1) {
        print_usage();
        return 0;
    }
    if (argc != 2) {
        print_usage();
        return 1;
    }
    if (strcmp(argv[1], "-t") == 0 || strcmp(argv[1], "--test") == 0) {
        return run_tests();
    }
    return 0;
}