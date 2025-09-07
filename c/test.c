/* All tests return 0 on success, 1 on failure. */
#include <string.h>
#include <stdio.h>
#include "parser.h"
#include "player.h"
#include "test.h"


int test_get_trainings_left(void) {
    Player_t p;
    Date_t cur_date;
    uint8_t res;
    memset(&p, 0, sizeof(p));

    p.bdate.week = 1;
    p.bdate.day = 1;
    cur_date.week = 5;
    cur_date.day = 5;

    if ((res = get_trainings_left(&p, cur_date)) != 9) {
        printf("%s failed. Expected %d, got %d.\n", __func__, 9, res);
        return 1;
    }
    return 0;
}

/* Since print_value_predictions() does not return anything,
   we cannot automatically check if the test passed. This
   is instead done via manual inspection (i.e., this test will
   always return 0). */
int test_print_value_predictions(void) {
    Player_t p = {0};
    Date_t cur_date;
    memset(&p, 0, sizeof(p));
    memcpy(p.name, "Tester McTester", sizeof("Tester McTester"));
    // p.name = "Tester McTester";
    p.pos = POS_F;
    p.value = 15000000;
    p.bdate.week = 2;
    p.bdate.day = 2;
    p.age = 18;
    cur_date.week = 1;
    cur_date.day = 1;
    p.transfer_list_idx = 69;
    p.bid = 1337420;
    p.has_bid = false;

    print_value_predictions(&p, cur_date);
    return 0;
}

int test_parse_transfer_list(void) {
    parse_transfer_list();
    return 0;
}