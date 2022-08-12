# Proxy

- `config-files` should be capable of a proxy and non-proxy environment
  - Ansible
    - The `group_vars` for `all` sets `proxy_environment` using e.g. `lookup("env","http_proxy")`
    - The `group_vars` directory is linked to the molecule default scenario for all roles
    - `proxy_environment` is used by all playbooks (`development` and molecule playbooks) as
      `environment: '{{ proxy_environment }}'`
    - If `lookup` does not find any proxy vars e.g. `http_proxy`, playbook(s) and roles should run either way
    - Proxy affected roles check for the proxy e.g. '{% if environment\[0\].http_proxy is defined and
      environment\[0\].http_proxy | length %}'
  - Molecule
    - All `molecule.yml` files are extended with env for proxies, so that the docker images can be build
    - They are disabled by default due to GitHub Travis CI, so please enable them if a proxy is used
