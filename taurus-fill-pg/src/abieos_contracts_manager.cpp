#include "abieos_contracts_manager.hpp"

std::string abieos_contracts_manager::abieos_hex_data_to_json(std::string contract_name, std::string type, std::string hex) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    const char *result = abieos_hex_to_json(context, contract_name_64, type.c_str(), hex.c_str());
    if(result){
        std::string res_str(result);
        return res_str;
    }else{
        //ilog("Failed to decode info: ${contract_name}", ("contract_name", contract_name));
    }

    return "";
}

std::string abieos_contracts_manager::abieos_kv_data_to_json(std::string contract_name, std::string key, std::string value) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());

    //TODO refactor this part, to not depend on these global buffers and simplify the logic
    const int LARGE_BUFFER_SIZE = 10'000'000;
    static char key_buffer[LARGE_BUFFER_SIZE];
    static char value_buffer[LARGE_BUFFER_SIZE];

    auto hex_char_to_number = [](char x) -> char{
        if(x <= '9') return x-'0';
        return x - 'A' + 10;
    };

    for(int i = 0;i < key.size(); i += 2)
        key_buffer[i>>1] = (hex_char_to_number(key[i])<<4) + hex_char_to_number(key[i+1]);


    for(int i = 0;i < value.size();i += 2)
        value_buffer[i>>1] = (hex_char_to_number(value[i])<<4) + hex_char_to_number(value[i+1]);

    const char *result = abieos_kv_bin_to_json(context, contract_name_64, key_buffer, key.size() >> 1, value_buffer, value.size() >> 1);

    if(result){
        std::string res_str(result);
        return res_str;
    }else{
        //ilog("Failed to decode info: ${contract_name}", ("contract_name", contract_name));
    }

    return "";
}

//TODO get rid of this method
std::string abieos_contracts_manager::abieos_hex_data_to_json_pg_copy_safe(std::string contract_name, std::string type, std::string hex) {
    std::string json_result = abieos_hex_data_to_json(contract_name, type, hex);

    int double_quote_counter = 0;
    for(int i = 0; i < json_result.size(); i++)
        if(json_result[i] == '"'){
            double_quote_counter++;
        }
        else if(json_result[i] == ','){
            if(double_quote_counter%2 == 1){
                json_result[i]=' ';
            }
        }
        else if(json_result[i] == '(' || json_result[i] == ')'){
                json_result[i] = ' ';
        }

    return json_result;
}

std::string abieos_contracts_manager::abieos_get_kv_table_type_data(std::string contract_name, std::string table_name) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    uint64_t table_name_64 = abieos_string_to_name(context, table_name.c_str());
    const char *result = abieos_get_type_for_kv_table(context, contract_name_64, table_name_64);
    if(result) {
        std::string res_str(result);
        return res_str;
    }
    else {
        return "";
    }
}

std::string abieos_contracts_manager::abieos_get_action_type(std::string contract_name, std::string action_name) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    uint64_t action_name_64 = abieos_string_to_name(context, action_name.c_str());
    const char *result = abieos_get_type_for_action(context, contract_name_64, action_name_64);
    if(result) {
        std::string res_str(result);
        return res_str;
    }
    else {
        return "";
    }
}

std::string abieos_contracts_manager::abieos_get_action_type_result(std::string contract_name, std::string action_name) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    uint64_t action_name_64 = abieos_string_to_name(context, action_name.c_str());
    const char *result = abieos_get_type_for_action_result(context, contract_name_64, action_name_64);
    if(result) {
        std::string res_str(result);
        return res_str;
    }
    else {
        return "";
    }
}

std::string abieos_contracts_manager::abieos_get_kv_table_primary_index_name_data(std::string contract_name, std::string table_name) {
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    uint64_t table_name_64 = abieos_string_to_name(context, table_name.c_str());
    const char *result = abieos_get_kv_table_primary_index_name(context, contract_name_64, table_name_64);
    if(result) {
        std::string res_str(result);
        return res_str;
    }
    else {
        return "";
    }
}

bool abieos_contracts_manager::abieos_set_contract_abi_hex(std::string contract_name, std::string abi_hex){
    uint64_t contract_name_64 = abieos_string_to_name(context, contract_name.c_str());
    auto success = abieos_set_abi_hex(context, contract_name_64, abi_hex.c_str());
    return success;
}

void abieos_contracts_manager::add_loaded_contract(std::string contract_name){
    contracts_loaded.push_back(contract_name);
}