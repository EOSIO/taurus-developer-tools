// copyright defined in LICENSE.txt

#pragma once
#include "state_history.hpp"
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#include <appbase/application.hpp>
#pragma clang diagnostic pop


class fill_plugin : public appbase::plugin<fill_plugin> {
  public:
    APPBASE_PLUGIN_REQUIRES()

    fill_plugin();
    virtual ~fill_plugin();

    virtual void set_program_options(appbase::options_description& cli, appbase::options_description& cfg) override;
    void         plugin_initialize(const appbase::variables_map& options);
    void         plugin_startup();
    void         plugin_shutdown();

    static std::vector<state_history::trx_filter> get_trx_filters(const appbase::variables_map& options);
};
