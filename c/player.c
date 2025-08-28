#include "player.h"

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

