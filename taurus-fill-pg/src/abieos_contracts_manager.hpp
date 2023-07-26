#pragma once

#include "util.hpp"
#include <eosio/abieos.h>
#include <eosio/abieos.hpp>

#include <string>
#include <map>
#include <filesystem>
#include <fstream>

class abieos_contracts_manager {
  private:
    abieos_context* context = nullptr;

    std::vector<std::string> contracts_loaded;

  public:

    abieos_contracts_manager() {
        if(!context){
            context = abieos_create();
        }
    }

    std::string abieos_hex_data_to_json(std::string contract_name, std::string type, std::string hex);

    std::string abieos_kv_data_to_json(std::string contract_name, std::string key, std::string value);

    std::string abieos_hex_data_to_json_pg_copy_safe(std::string contract_name, std::string type, std::string hex);

    std::string abieos_get_kv_table_type_data(std::string contract_name, std::string table_name);

    std::string abieos_get_action_type(std::string contract_name, std::string action_name);

    std::string abieos_get_action_type_result(std::string contract_name, std::string action_name);

    std::string abieos_get_kv_table_primary_index_name_data(std::string contract_name, std::string table_name);

    bool abieos_set_contract_abi_hex(std::string contract_name, std::string abi_hex);

    void add_loaded_contract(std::string contract_name);

    std::vector<std::string> get_loaded_contract_names() {
        return contracts_loaded;
    }
};
