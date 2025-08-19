Appendix A.7 3GPP NRM emulation

# NRM emulation server
The connexion subfolder holds the NRM server code and the specifications it uses for handling SEAL requests.
The SEAL request are OpenAPI specifications in YAML format, which can be found in the "connexion/connexion-example-master/yaml" folder.
The NRM server is written using Connexion, which allows for API first development.

# The implemented SEAL functions:
- Group Management
- Network Resource Adaptation
- Location Reporting
- Location Area Info Retrieval

[A bit more in depth breakdown of codes and structure](<connexion/README.md>)