#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "player.h"

#define LEN_WEEKLY_INCREASES 5
#define MAX_PREDICT_AGE 23  /* Change this when adding more entries. */
#define DIVIDER "--------------------\n"

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

/* Used to store "pretty" versions of player values or bids. */
char pretty_buf[MAX_BUF_LEN_VALUE_STR];

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
        case POS_G: return "Goalie";
        case POS_D: return "Defender";
        case POS_F: return "Forward";
        case POS_INV:
            /* Fallthrough */
        default:
            return "?";
    }
}

/* Transforms player value or bid to a printable string.
   `add_parens` true when printing starting bid. */
static void value_to_str(const unsigned int value, const bool add_parens) {
    size_t num_starting_digits = 0;
    char raw_buf[MAX_BUF_LEN_VALUE] = "";   /* Max 10 digits + null byte. */
    char *raw_buf_ptr;

    snprintf(raw_buf, MAX_BUF_LEN_VALUE, "%u", value);
    num_starting_digits = strnlen(raw_buf, MAX_BUF_LEN_VALUE) % 3;
    raw_buf_ptr = &raw_buf[0];
    memset(pretty_buf, 0, MAX_BUF_LEN_VALUE_STR);

    if (add_parens) {
        /* Add parenthesis if we are printing a starting bid. */
        pretty_buf[0] = '(';
    }
    /* We want to transform raw_buf for example like this:
       7500000 -> 7 500 000 kr. @todo: is there a better way of doing this? */
    #pragma GCC diagnostic push
    #pragma GCC diagnostic ignored "-Wstringop-truncation"
    strncat(pretty_buf, raw_buf_ptr, num_starting_digits);
    #pragma GCC diagnostic pop

    raw_buf_ptr += num_starting_digits;
    if (num_starting_digits) {
        /* We don't want leading spaces, so check that we have
           added digits. */
        strncat(pretty_buf, " ", 1);
    }

    while (*raw_buf_ptr != '\0') {
        strncat(pretty_buf, raw_buf_ptr, 3);
        strncat(pretty_buf, " ", 1);
        raw_buf_ptr += 3;
    }
    /* No more digits to transfer to pretty_buf. */
    strncat(pretty_buf, "kr", 2);
    if (add_parens) {
        /* Close the parenthesis on the starting bid. */
        strncat(pretty_buf, ")", 1);
    }
}

/* Prints name, position, age and value of the given player.
   If the player is transferlisted, print (starting)bid. */
void print_player_info(const Player_t *p) {
    value_to_str(p->value, false);
    printf("%s, %s, %u\n", p->name, pos_to_str(p->pos), p->age);
    printf("Value: %s\n", pretty_buf);
    if (p->transfer_list_idx) {
        value_to_str(p->bid, !p->has_bid);
        printf("Current bid: %s\n", pretty_buf);
    }
}

/* Based on how many more training opportunities the player has,
   in combination with his age, try to predict the player value at the
   end of the current player age. At the end, print those predictions. */
void print_value_predictions(const Player_t *p, const Date_t cur_date) {
    const unsigned int *w;
    size_t i;
    uint8_t trainings = get_trainings_left(p, cur_date);

    if (p->age > MAX_PREDICT_AGE) {
        return;
    }
    print_player_info(p);
    printf(DIVIDER);
    for (w = *weekly_increases; w != NULL; w += LEN_WEEKLY_INCREASES) {
        if (*w != p->age) {
            /* Loop until we find the correct age. */
            continue;
        }
        for (i = 1; i < LEN_WEEKLY_INCREASES; i++) {
            value_to_str(w[i], false);
            printf("%s / w: ", pretty_buf);
            value_to_str(p->value + trainings * w[i], false);
            printf("%s\n", pretty_buf);
        }
        break;
    }
    printf("%s\n", DIVIDER);
}
