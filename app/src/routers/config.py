class APIV1PrefixConfig:
    prefix: str = "/v1"
    ddu_contractors: str = "/ddu_contractors"


class APIPrefixConfig:
    prefix: str = "/api"
    v1: APIV1PrefixConfig = APIV1PrefixConfig()


api_prefix_config = APIPrefixConfig()
