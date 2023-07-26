#pragma once

#include <eosio/stream.hpp>
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-copy"
#include <boost/iostreams/device/back_inserter.hpp>
#include <boost/iostreams/filter/zlib.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#pragma clang diagnostic pop
#include <fstream>

inline std::string read_string(const char* filename) {
    try {
        std::fstream file(filename, std::ios_base::in | std::ios_base::binary);
        file.seekg(0, std::ios_base::end);
        auto len = file.tellg();
        file.seekg(0, std::ios_base::beg);
        std::string result(len, 0);
        file.read(result.data(), len);
        return result;
    } catch (const std::exception& e) {
        throw std::runtime_error("Error reading " + std::string(filename));
    }
}

inline std::vector<char> zlib_decompress(eosio::input_stream data) {
    std::vector<char>                   out;
    boost::iostreams::filtering_ostream decomp;
    decomp.push(boost::iostreams::zlib_decompressor());
    decomp.push(boost::iostreams::back_inserter(out));
    boost::iostreams::write(decomp, data.pos, data.end - data.pos);
    boost::iostreams::close(decomp);
    return out;
}

inline uint64_t name_hex_to_value(std::string s){
    uint64_t result = 0;
    for(int i=0;i < s.size();i++){
        result = result * 16;
        switch(s[i]){
        case 'A': result += 10; break;
        case 'B': result += 11; break;
        case 'C': result += 12; break;
        case 'D': result += 13; break;
        case 'E': result += 14; break;
        case 'F': result += 15; break;
        default: result += (s[i]-'0'); break;
        }
    }
    return result;
}

template <typename SrcIt, typename DestIt>
inline bool unhex(SrcIt begin, SrcIt end, DestIt dest) {
    auto get_digit = [&](uint8_t& nibble) {
        if (*begin >= '0' && *begin <= '9')
            nibble = *begin++ - '0';
        else if (*begin >= 'a' && *begin <= 'f')
            nibble = *begin++ - 'a' + 10;
        else if (*begin >= 'A' && *begin <= 'F')
            nibble = *begin++ - 'A' + 10;
        else
            return false;
        return true;
    };
    while (begin != end) {
        uint8_t h, l;
        if (!get_digit(h) || !get_digit(l))
            return false;
        *dest++ = (h << 4) | l;
    }
    return true;
}
