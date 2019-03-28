# Server settings

The service is configured via a simple configuration file encoded using
[TOML][].

[TOML]: https://github.com/toml-lang/toml

```toml
[chaosplatform]
debug = false

    [chaosplatform.http]
    address = "0.0.0.0:8090"
    secret_key = ""

        [chaosplatform.http.tls]
        certificate = ""
        key = ""

        [chaosplatform.http.cherrypy]
        proxy = "http://localhost:6080"
        environment = "production"

    [chaosplatform.cache]
    type = "simple"

    [chaosplatform.db]
    uri = "sqlite:///:memory:"

    [chaosplatform.jwt]
    secret_key = ""
    public_key = ""
    algorithm = "HS256"
    identity_claim_key = "identity"
    user_claims_key = "user_claims"
    access_token_expires = 2592000
    refresh_token_expires = 1800
    user_claims_in_refresh_token = true
        
    [chaosplatform.grpc]
    address = "0.0.0.0:50051"

        [chaosplatform.grpc.auth]
        address = "0.0.0.0:50052"

        [chaosplatform.grpc.activity]
        address = "0.0.0.0:50053"

        [chaosplatform.grpc.scheduling]
        address = "0.0.0.0:50054"
```

## [chaosplatform] section

This is the toplevel section of that file and must always be present.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|----------------------------------------------------|
| debug                     | false             | No       | Enable more traces |


## [chaosplatform.http] section

To configure the HTTP server.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| address                   | "0.0.0.0:8090"    | Yes      | Address to which listen to |
| secret_key                | ""                | Yes      | The secret value used to sign session cookies. Keep it safe and secret |

## [chaosplatform.http.tls] section

An optional section to set the HTTP server to use TLS. If you don't need TLS,
simply remove or comment out this section.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| certificate               | ""                | Yes      | The path to the certificate |
| key                       | ""                | Yes      | They private key path |

For development or local development, you may use [mkcert][].

[mkcert]: https://github.com/FiloSottile/mkcert

## [chaosplatform.http.cherrypy] section

To configure the default [CherryPy][cherrypy] HTTP server.

[cherrypy]: https://cherrypy.org/

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| proxy                     | ""                | No       | The base URL of any reverse-proxy in fron of the service |
| environment               | "production"      | No       | The default settings of the CherryPy server |

## [chaosplatform.cache] section

To configure the [caching][] of the application.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| type                      | "simple"          | Yes      | The type of cahcing to use |

[caching]: https://pythonhosted.org/Flask-Caching/

## [chaosplatform.db] section

To configure the database connection.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| uri                       | "sqlite:///:memory:"    | Yes      | Connection [URI][dburi] |

[dburi]: https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls


## [chaosplatform.jwt] section

To configure the [JWT engine][jwt] for the access tokens.


| Key                           | Default           | Required | Description                                        | 
|-------------------------------|-------------------|----------|--------------------------- |
| secret_key                    | ""    | Yes      |  |
| public_key                    | ""    | Yes      |  |
| algorithm                     | "HS256"    | Yes      |  |
| identity_claim_key            | "identity"    | Yes      |  |
| user_claims_key               | "user_claims"    | Yes      |  |
| access_token_expires          | 2592000    | Yes      | |
| refresh_token_expires         | 1800    | Yes      |  |
| user_claims_in_refresh_token  | true    | Yes      |  |

[jwt]: https://flask-jwt-extended.readthedocs.io/en/latest/options.html


## [chaosplatform.grpc] section

To configure the gRPC endpoints.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| address                   | "0.0.0.0:50051"    | Yes      | Listen for gRPC requests on this address |

## [chaosplatform.grpc.auth] section

To configure the gRPC authentication gRPC service access.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| address                   | "0.0.0.0:50052"    | Yes      | Address of the authentication service |

## [chaosplatform.grpc.activity] section

To configure the gRPC activity gRPC service access.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| address                   | "0.0.0.0:50052"    | Yes      | Address of the activity service |

## [chaosplatform.grpc.scheduling] section

To configure the gRPC scheduling gRPC service access.

| Key                       | Default           | Required | Description                                        | 
|---------------------------|-------------------|----------|--------------------------- |
| address                   | "0.0.0.0:50052"    | Yes      | Address of the scheduling service |
