#include <iostream>
#include <string>
#include <iostream>
#include <random>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

#define X uuid << "-";

string generateRandomUUID()
{
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distrib(0, 15);

    stringstream uuid;

    for (int i = 0; i < 8; ++i)
        uuid << hex << distrib(gen);

    X

        for (int i = 0; i < 4; ++i)
            uuid
        << hex << distrib(gen);

    X

        for (int i = 0; i < 4; ++i)
            uuid
        << hex << distrib(gen);

    X

        for (int i = 0; i < 4; ++i)
            uuid
        << hex << distrib(gen);

    X

        for (int i = 0; i < 12; ++i)
            uuid
        << hex << distrib(gen);

    return uuid.str();
}

int main(int argc, char **argv)
{
    string title;
    string uuid = generateRandomUUID();

    cout << "Input title: ";
    cin >> title;
    if (title.empty())
    {
        cerr << "No title, give up" << endl;
        return 1;
    }

    fs::path rootDir = "src/articles";
    fs::path fileName = title.append(".md");
    fs::path fullPath = rootDir / fileName;

    cout << "Full path: " << fullPath << std::endl;

    if (fs::exists(fullPath))
    {
        cerr << "File exists. Abort." << endl;
        return 2;
    }
    else
    {
        /** create .md file */
        ofstream ofs(fullPath, ofstream::out);
        if (!ofs)
        {
            cerr << "Error: failed to create file." << endl;
            return 3;
        }

        ofs << R"(---
uuid: ")" << uuid
            << R"("
title: ")" << title
            << R"("
subtitle: "这里输入副标题，删除此项则使用日期"
english: "英文标题，用于 URL 以避免长长的中文转义符"
date: ")" << __DATE__
            << R"("
category: "分类"
project: "专栏，若无则删除此行"
outdated: false
draft: false
ref: 
  - name: "第一个参考链接"
    url: "www.example_1.com"
---)";
        ofs.flush();
        ofs.close();
    }

    return 0;
}