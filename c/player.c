#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "player.h"

#define LEN_WEEKLY_INCREASES 5
#define MAX_BUF_LEN_VALUE 11      /* Max e.g. "9999999999". */
#define MAX_BUF_LEN_VALUE_STR 19  /* Max e.g. "(9 999 999 999 kr)". */
#define MAX_PREDICT_AGE 23        /* Change this when adding more entries. */

/* Age, followed by pontential weekly increase values. */
const unsigned int weekly_increases[][LEN_WEEKLY_INCREASES] = {
    {17, 300000, 350000, 400000, 500000},
    {18, 400000, 450000, 500000, 600000},
    {19, 500000, 600000, 700000, 800000},
    {20, 700000, 800000, 900000, 1000000},
    {21, 800000, 900000, 1000000, 1100000},
    {22, 900000, 1000000, 1100000, 1200000},
    {23, 1000000, 1100000, 1200000, 1300000},
};

/* Calculates the number of training opportunities left before
   player turns one year older. */
uint8_t get_trainings_left(const Player_t *p, const Date_t cur_date) {
    /* Add MAX_WEEKS before taking the remainder to avoid negative
       training opportunities incase current week > birth week. */
    uint8_t dose_reset, last_training, weeks;
    weeks = (p->bdate.week - cur_date.week + MAX_WEEKS) % MAX_WEEKS;
    if (weeks == 0 && cur_date.day > p->bdate.day) {
        /* This happens if the player already has turned one year older,
           but we are still in his birth week. */
        weeks = MAX_WEEKS;
    }
    dose_reset = cur_date.day == MAX_DAYS;
    last_training = p->bdate.day == MAX_DAYS;
    return weeks + dose_reset + last_training;
}

static const char *pos_to_str(const Position_t pos) {
    switch (pos) {
        case POS_G:
            return "G";
        case POS_D:
            return "D";
        case POS_F:
            return "F";
        case POS_INV:
        default:
            return "?";
    }
}

/* Transforms player value or bid to a printable string.
   add_parens only used when printing starting bid. */
static void value_to_str(const Player_t *p, const bool bid, char *pretty_buf) {
    size_t num_starting_digits = 0;
    char raw_buf[MAX_BUF_LEN_VALUE] = "";   /* Max 10 digits + null byte. */
    char *raw_buf_ptr;

    snprintf(raw_buf, MAX_BUF_LEN_VALUE, "%u", bid ? p->bid : p-> value);
    num_starting_digits = strnlen(raw_buf, MAX_BUF_LEN_VALUE) % 3;
    raw_buf_ptr = &raw_buf[0];


    if (bid && !p->has_bid) {
        /* Add parenthesis if we are printing a starting bid. */
        pretty_buf[0] = '(';
    }
    /* We want to transform raw_buf for example like this:
       7500000 -> 7 500 000 kr.  */
    #pragma GCC diagnostic push
    #pragma GCC diagnostic ignored "-Wstringop-truncation"
    strncat(pretty_buf, raw_buf_ptr, num_starting_digits);
    #pragma GCC diagnostic pop

    raw_buf_ptr += num_starting_digits;
    strncat(pretty_buf, " ", 1);

    while (*raw_buf_ptr != '\0') {
        strncat(pretty_buf, raw_buf_ptr, 3);
        strncat(pretty_buf, " ", 1);
        raw_buf_ptr += 3;
    }
    /* No more digits to transfer to pretty_buf! */
    strncat(pretty_buf, "kr", 2);
    if (bid && !p->has_bid) {
        /* Close the parenthesis on the starting bid. */
        strncat(pretty_buf, ")", 1);
    }
}

/* Based on how many more training opportunities the player has,
   in combination with his age, try to predict the player value at the
   end of the current player age. At the end, print those predictions. */
void print_value_predictions(const Player_t *p, const Date_t cur_date) {
    char value_buf[MAX_BUF_LEN_VALUE_STR] = "";
    char bid_buf[MAX_BUF_LEN_VALUE_STR] = "";
    uint8_t trainings = get_trainings_left(p, cur_date);
    const char *pos_str = pos_to_str(p->pos);
    const unsigned int *w;
    size_t i;

    if (p->transfer_list_idx == 0) {
        /* This player was parsed from a roster. */
        printf("%s - %s, %" PRIu8 "\n", pos_str, p->name, p->age);
    }
    else {
        value_to_str(p, !p->has_bid, bid_buf);
        printf("%u. %s - %s, %" PRIu8 ", %s\n",
            p->transfer_list_idx, pos_str, p->name, p->age, bid_buf);
    }
    value_to_str(p, false, value_buf);
    printf("Current value: %s\n", value_buf);

    if (p->age > MAX_PREDICT_AGE) {
        printf("%s is too old, skipping prediction.\n", p->name);
        return;
    }
    for (w = *weekly_increases; w != NULL; w += LEN_WEEKLY_INCREASES) {
        if (*w != p->age) {
            /* Loop until we find the correct age. */
            continue;
        }
        for (i = 1; i < LEN_WEEKLY_INCREASES; i++) {
            printf("%u/w: %u kr\n", w[i], p->value + trainings * w[i]);
        }
        break;
    }
}
