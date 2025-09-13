#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.h"
#include "test.h"

static int run_tests(void) {
    if (test_get_trainings_left()) return 1;
    if (test_print_value_predictions()) return 1;  /* Manual inspection of output. */
    if (test_parse_transfer_list()) return 1;      /* Manual inspection of output. */
    printf("All tests passed.\n");
    return 0;
}

static void print_usage(void) {
    printf("----- lhutils -----\n\n");
    printf("Usage: ./lhutils [OPTION]\n");
    printf("[OPTION]:\n\n");
    printf("-h, --help\n");
    printf("\t\tPrint this information and exit.\n\n");
    printf("-t, --test\n");
    printf("\t\tRun all unit tests.\n\n");
    printf("-tl, --transfer-list\n");
    printf("\t\tParse transferlist and output predicted values.\n\n");
}

int main(int argc, char **argv) {
    /* Parse arguments. */
    if (argc == 1) {
        print_usage();
        return EXIT_SUCCESS;
    }
    if (argc != 2) {
        print_usage();
        return EXIT_FAILURE;
    }
    if (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0) {
        print_usage();
        return EXIT_SUCCESS;
    }
    if (strcmp(argv[1], "-t") == 0 || strcmp(argv[1], "--test") == 0) {
        return run_tests();
    }
    if (strcmp(argv[1], "-tl") == 0 || strcmp(argv[1], "--transfer-list") == 0) {
        return parse_transfer_list();
    }
    printf("Unrecognized argument: %s\n", argv[1]);
    print_usage();
    return EXIT_FAILURE;
}