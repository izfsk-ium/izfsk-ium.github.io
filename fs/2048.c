#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ncurses.h>

#define MATRIX_SIZE 5
#define RAND_POSITION() (rand()) % (MATRIX_SIZE + 1)
#define PRINT_TYPE(X)                 \
    {                                 \
        (attron(X));                  \
        printw("%4d ", matrix[i][j]); \
        attroff(X);                   \
    }

int matrix[MATRIX_SIZE][MATRIX_SIZE] = {0};
int step_counter = 0;
int character_input;

int get_max_number()
{
    int max = matrix[0][0];
    for (int i = 0; i < MATRIX_SIZE; i++)
        for (int j = 0; j < MATRIX_SIZE; j++)
            max = matrix[i][j] > max ? matrix[i][j] : max;
    return max;
}

int print_matrix()
{
    refresh();
    if (get_max_number() == 2048)
    {
        attron(A_REVERSE);
        mvprintw(0, 0, "YOU WIN!");
        attroff(A_REVERSE);
        return 0;
    }
    mvprintw(0, 0, "[%d]Step: %d\n", get_max_number(), step_counter);
    for (int i = 0; i < MATRIX_SIZE; i++)
    {
        for (int j = 0; j < MATRIX_SIZE; j++)
        {
            switch (matrix[i][j])
            {
            case 4:
            case 8:
                PRINT_TYPE(A_BOLD);
                break;
            case 16:
            case 32:
                PRINT_TYPE(A_BOLD | A_UNDERLINE);
                break;
            case 64:
            case 128:
                PRINT_TYPE(A_REVERSE | A_BOLD);
                break;
            case 256:
            case 512:
                PRINT_TYPE(A_REVERSE | A_BOLD | A_UNDERLINE);
                break;
            case 1024:
            case 2048:
                PRINT_TYPE(A_REVERSE | A_BOLD | A_UNDERLINE | A_BLINK);
                break;
            default:
                printw("%4d ", matrix[i][j]);
                break;
            }
        }
        printw("\n");
    }
    printw("Use w,a,s,d to move, q to quit...");
    return getch();
}

int put_random_number()
{
    int x = 0, y = 0, counter = 0;
    do
    {
        x = RAND_POSITION();
        y = RAND_POSITION();
    } while (matrix[x][y] != 0 && ++counter != (MATRIX_SIZE * MATRIX_SIZE));
    if (counter == MATRIX_SIZE * MATRIX_SIZE)
    {
        printw("Nowhere to put !");
        return 0;
    }
    matrix[x][y] = 2;
    return 1;
}

void reverse_range(int *array, int left, int right)
{
    while (left < right)
    {
        int temp = array[left];
        array[left++] = array[right];
        array[right--] = temp;
    }
}

void process_addition(int *tmp_array)
{
    int *ptr_end_a = tmp_array + MATRIX_SIZE - 1,
        *ptr_end_b = tmp_array + MATRIX_SIZE - 2;
    for (int i = 0; i < MATRIX_SIZE - 2; i++)
    {
        if (*ptr_end_a == *ptr_end_b)
        {
            *ptr_end_a = *ptr_end_a + *ptr_end_b;
            *ptr_end_b = 0;
        }
        if (*ptr_end_a == 0 && *ptr_end_b != 0)
        {
            int tmp = *ptr_end_b;
            *ptr_end_b = *ptr_end_a;
            *ptr_end_a = tmp;
        }
        ptr_end_a--;
        ptr_end_b--;
    }
}

void action_move_W()
{
    for (int col = 0; col < MATRIX_SIZE; col++)
    {
        int tmp[MATRIX_SIZE] = {0}, no_zero_counter = 0;
        for (int row = 0; row < MATRIX_SIZE; row++)
            if (matrix[row][col] != 0)
                tmp[no_zero_counter++] = matrix[row][col];
        reverse_range(tmp, 0, MATRIX_SIZE - 1);
        process_addition(tmp);
        reverse_range(tmp, 0, MATRIX_SIZE - 1);
        for (int i = 0; i < MATRIX_SIZE; i++)
            matrix[i][col] = tmp[i];
    }
}

void action_move_S()
{
    for (int col = 0; col < MATRIX_SIZE; col++)
    {
        int tmp[MATRIX_SIZE] = {0}, no_zero_counter = 0;
        for (int row = 0; row < MATRIX_SIZE; row++)
            if (matrix[row][col] != 0)
                tmp[no_zero_counter++] = matrix[row][col];
        for (int i = 0; i < MATRIX_SIZE - no_zero_counter; i++)
        {
            int temp = tmp[MATRIX_SIZE - 1];
            for (int j = MATRIX_SIZE - 1; j >= 0; j--)
                tmp[j] = tmp[j - 1];
            tmp[0] = temp;
        }
        process_addition(tmp);
        for (int i = 0; i < MATRIX_SIZE; i++)
            matrix[i][col] = tmp[i];
    }
}

void action_move_A()
{
    for (int row = 0; row < MATRIX_SIZE; row++)
    {
        int tmp[MATRIX_SIZE] = {0}, no_zero_counter = 0;
        for (int col = 0; col < MATRIX_SIZE; col++)
            if (matrix[row][col] != 0)
                tmp[no_zero_counter++] = matrix[row][col];
        reverse_range(tmp, 0, MATRIX_SIZE - 1);
        process_addition(tmp);
        reverse_range(tmp, 0, MATRIX_SIZE - 1);
        for (int i = 0; i < MATRIX_SIZE; i++)
            matrix[row][i] = tmp[i];
    }
}

void action_move_D()
{
    for (int row = 0; row < MATRIX_SIZE; row++)
    {
        int tmp[MATRIX_SIZE] = {0}, no_zero_counter = 0;
        for (int col = 0; col < MATRIX_SIZE; col++)
            if (matrix[row][col] != 0)
                tmp[no_zero_counter++] = matrix[row][col];
        // right shift the array from [X, Y, 0, 0, 0] to [0, 0, 0, X, Y]
        for (int i = 0; i < MATRIX_SIZE - no_zero_counter; i++)
        {
            int temp = tmp[MATRIX_SIZE - 1];
            for (int j = MATRIX_SIZE - 1; j >= 0; j--)
                tmp[j] = tmp[j - 1];
            tmp[0] = temp;
        }
        // process addition and overwrite matrix
        process_addition(tmp);
        for (int i = 0; i < MATRIX_SIZE; i++)
            matrix[row][i] = tmp[i];
    }
}

int main(int argc, char *argv[])
{
    initscr();
    raw();
    keypad(stdscr, TRUE);
    noecho();
    srand(time(NULL));

    while (character_input != 'q' && put_random_number() && ++step_counter)
    {
        character_input = print_matrix();
        switch (character_input)
        {
        case 'w':
            action_move_W();
            break;
        case 'a':
            action_move_A();
            break;
        case 's':
            action_move_S();
            break;
        case 'd':
            action_move_D();
            break;
        default:
            break;
        }
    }

    refresh();
    clear();
    printw("You lost! (steps:%d with %d.)\nPress any key to exit.", step_counter, get_max_number());
    getch();
    endwin();
    return 0;
}