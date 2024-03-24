#include "iostream"
#include "string"
#include "limits"

void appendHexToString(std::string& str, int n) {
    static const char* DIGITS = "0123456789abcdef";
    for(int i = 0; i < 8; i++) {
        int digitIndex = (n & 0xf0000000) >> 28;
        str += DIGITS[digitIndex];
        n = n << 4;
    }
    if( str.length()%18 == 17 ) {
        str += "\n";
    } else {
        str += " ";
    }
}

/*
* Convert address to 04 codetype
*/
int to04code(int n) {
    n = (n & 0x00ffffff) | 0x04000000;
    return n;
}

int toRGBcode(int r, int g, int b) {
    return (r << 16) | (g << 8) | b;
}

int selectRegion() {
    // Ask for region
    std::cout << "Select region\n"
    << "1. PAL, Revision 1\n"
    << "2. PAL, Revision 2\n"
    << "3. NTSC-U\n";
    int input;
    while(true) {
        std::cin >> input;
        if(input >= 1 && input <= 3)
            break;
        std::cout << "Invalid input";
    }

    switch(input) {
    case 1:
        return 0x80504d00;
    case 2:
        return 0x80505280;
    case 3:
        return 0x80505990;
    default:
        return 0x80504d00;
    }
}

int main() {
    int firstAddr = selectRegion();
    // Infinite loop
    while(true) {
        int input;
        // Ask the user what character they want to create a gecko code for
        while(true) {
            std::cout << "\nSelect a character by typing the corresponding number\n"
            << "1. Mario\n"
            << "2. Bowser\n"
            << "3. Daisy\n"
            << "4. DK\n"
            << "5. Luigi\n"
            << "6. Peach\n"
            << "7. Waluigi\n"
            << "8. Wario\n"
            << "9. Yoshi\n"
            << "10. Bowser jr.\n"
            << "11. Diddy kong\n"
            << "12. Petey\n"
            << "or else press 0 to return to the region selection\n";
            std::cin >> input;
            if(input >= 1 && input <= 12) {
                break;
            } else if(input == 0) {
                firstAddr = selectRegion();
            }
            std::cout << "Invalid input!";
        }
        // increment the address by 0x5c times the character's ID
        int charAddr = firstAddr + 0x5c*(input - 1);

        // Ask the user what they want to change about the character
        do{
            std::cout << "\nWhat do you want to do?\n";
            std::cout << "1. edit the character's color flags\n";
            std::cout << "2. edit the character's color priority\n";
            std::cout << "3. edit the character's indicator RGB color\n";
            std::cin >> input;
        }while(input < 1 || input > 3);

        // Ask te user what values they want
        int addrToManipulate;
        int flags = 0;
        std::string output = "";
        switch(input) {
            case 1:
                addrToManipulate = charAddr;
                appendHexToString(output, to04code(addrToManipulate));
                while(true) {
                    std::cout << "\nInsert the number of the flag to toggle, or insert 0 when you're done\n"
                    << "1. RED\n"
                    << "2. GREEN\n"
                    << "3. PINK\n"
                    << "4. PURPLE\n"
                    << "5. YELLOW\n"
                    << "6. custom flag 1 (BLUE)\n"
                    << "7. custom flag 2 (WHITE)\n"
                    << "8. custom flag 3 (BLACK)\n"
                    << "9 through 32. Other custom flags\n";
                    std::cin >> input;
                    if(input == 0)
                        break;
                    int bitToAlter = 0x00000001;
                    bitToAlter <<= input-1;
                    flags ^= bitToAlter;
                    std::cout << (flags & bitToAlter ? "FLAG ENABLED" : "FLAG DISABLED") << "\n\n";
                }
                appendHexToString(output, flags);
                break;                
            case 2:
                addrToManipulate = charAddr + 0x4;
                appendHexToString(output, to04code(addrToManipulate));
                int prio;
                std::cout << "Insert the priority value (The lower the number, the higher the priority)";
                std::cin >> prio;
                appendHexToString(output, prio);
                break;
            case 3:
                std::cout << "Which skin?\n1. Primary\n2. Secondary\n";
                while(true) {
                    std::cin >> input;
                    if(input == 1 || input == 2)
                        break;
                    std::cout << "invalid input";
                }
                if(input == 1)
                    addrToManipulate = charAddr + 0x8;
                if(input == 2)
                    addrToManipulate = charAddr + 0xc;
                appendHexToString(output, to04code(addrToManipulate));
                int colors[3];
                for(int i = 0; i < 3; i++) {
                    std::string colorName;
                    switch(i) {
                    case 0:
                        colorName = "Red";
                        break;
                    case 1:
                        colorName = "Green";
                        break;
                    case 2:
                        colorName = "Blue";
                        break;
                    }
                    std::cout << "How much " << colorName << "? (insert number between 0 and 255 included)\n";
                    while(true) {
                        std::cin >> input;
                        if(input >= 0 && input <= 255)
                            break;
                        std::cout << "invalid input\n";
                    }
                    colors[i] = input;
                }
                appendHexToString(output, toRGBcode(colors[0], colors[1], colors[2]));
                break;
        }

        std::cout << "\n\n\nHere's your gecko code:\n"<< output << "\n\n\n";
        std::cout << "Press Enter to Continue";
        std::cin.get();
        std::cin.ignore();

    }

    return 0;
}
