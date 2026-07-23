# Proxy

- `config-files` should be capable of a proxy and non-proxy environment
  - Ansible
    - The `group_vars` for `all` sets `proxy_environment` using e.g. `lookup("env","http_proxy")`
    - The `group_vars` directory is linked to the molecule default scenario for all roles
    - `proxy_environment` is used by all playbooks (`development` and molecule playbooks) as
      `environment: '{{ proxy_environment }}'`
    - If `lookup` does not find any proxy vars e.g. `http_proxy`, playbook(s) and roles should run either way
    - Proxy affected roles check for the proxy e.g. '{% if environment[0].http_proxy is defined and
      environment[0].http_proxy | length %}'
  - Molecule
    - The default `molecule.yml` does not set proxy build arguments or container environment variables
    - `cf-molecule` detects loopback proxy URLs in `http_proxy` or `https_proxy`
    - If a loopback proxy is detected, `cf-molecule` creates a temporary Molecule scenario with proxy build arguments,
      container environment variables, and host networking
