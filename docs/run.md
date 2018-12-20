# Run the Service

The service can be run a standalone microservice or can be embedded into
a larger component. This page describes the former.

You may run this service without any further dependency. From your virtual
environment, run the following command:

```
$ chaosplatform-account run
```

You should pass the settings as follows:


```
$ chaosplatform-account run --env-path=.env
```

Read the [settings][] documentation to know what values can be set.

[settings]: ./settings.md


## Dependencies

The authentication service expects to find the account service via gRPC so it
can create accounts.

