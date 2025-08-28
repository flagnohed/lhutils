#include <string.h>
#include <stdio.h>
#include "test.h"
#include "player.h"

/* Returns 0 on success, 1 on failure. */
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