#include "ret.h"

bool is_ret_ok(ret_t ret_value) {
    return ret_value == RET_OK;
}

bool is_ret_arg_err(ret_t ret_value) {
    return ret_value / 100 == (RET_ARG_ERR / 100);
}

bool is_ret_internal_err(ret_t ret_value) {
    return ret_value / 100 == (RET_INTERNAL_ERR / 100);
}

bool is_ret_errno_err(ret_t ret_value) {
    return ret_value == RET_ERRNO_ERR;
}

bool is_ret_err(ret_t ret_value) {
    return is_ret_arg_err(ret_value) || is_ret_internal_err(ret_value) || is_ret_errno_err(ret_value);
}

bool is_ret_custom(ret_t ret_value) {
    return ret_value / 100 == (RET_CUSTOM / 100);
}
