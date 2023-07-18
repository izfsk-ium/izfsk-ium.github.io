#include <iostream>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <vector>
#include <algorithm>

namespace fs = std::filesystem;

extern std::string sha224(void *);

int main()
{
    int sum = 0;

    // Iterate over all '.md' files in 'src/articles'
    for (const auto &entry : fs::recursive_directory_iterator("src/articles"))
    {
        if (entry.is_regular_file() && entry.path().extension() == ".md")
        {
            std::string file = entry.path().string();

            // Get the old hash from 'chksum.list'
            std::ifstream chksumFile("chksum.list");
            std::string line;
            std::string old_hash;
            while (std::getline(chksumFile, line))
            {
                if (line.find(file) != std::string::npos)
                {
                    std::istringstream iss(line);
                    iss >> old_hash;
                    break;
                }
            }

            // Calculate the new hash
            std::ifstream fileStream(file, std::ios::binary);
            std::stringstream ss;
            ss << fileStream.rdbuf();
            std::string new_hash = sha224(ss.str()).substr(0, 56);

            // Compare old and new hash
            if (old_hash == new_hash)
            {
                // Do nothing (equivalent of ":")
            }
            else
            {
                ++sum;
                std::cout << file << " ";
            }
        }
    }

    if (sum == 0)
    {
        std::cout << "Abort" << std::endl;
        return 1;
    }

    return 0;
}