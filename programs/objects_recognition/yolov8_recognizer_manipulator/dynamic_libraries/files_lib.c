#include <stdio.h>
#include <stdlib.h>
#include <string.h>

short check_for_img_command(const char* path,
							const char* get_img_command) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        printf("File '%s' not found.\n", path);
        return 0;
    }

    char line[256];
    short found = 0;

    while (fgets(line, sizeof(line), file)) {
        if (strstr(line, get_img_command) != NULL) {
            found = 1;
            break;
        }
    }
    fclose(file);

    if (found) {
        file = fopen(path, "w");
        if (file != NULL) {
            fclose(file);
        }
        return 1;
    }

    return 0;
}

char* read_word(const char *path) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        printf("File reading error: cannot open \"%s\".\n", path);
        return NULL;
    }

    char *buffer = (char *)malloc(256 * sizeof(char));
    if (buffer == NULL) {
        printf("Memory allocation error.\n");
        fclose(file);
        return NULL;
    }

    if (fgets(buffer, 256, file) == NULL) {
        free(buffer);
        fclose(file);
        return NULL;
    }

    //buffer[strcspn(buffer, "\r\n")] = '\0';

    fclose(file);
    return buffer;
}


/* int main(void) {
    const char *file_path = "test.txt";
    printf("%d", check_for_img_command(file_path, "<TSC>"));
    return EXIT_SUCCESS;
} */
