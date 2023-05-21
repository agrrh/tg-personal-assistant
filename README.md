# tg-personal-assistant

- Consumes events from NATS JetStream topic
- Handles the logic
- Sends events back for tg-dispatcher to process replies

## Design

```mermaid
graph LR
  actor((actor))
  telegram

  subgraph bus
    personal-assistant.tg.in
    personal-assistant.tg.out
  end

  subgraph kubernetes
    subgraph tg-components
      tg-consumer
      tg-sender
    end

    subgraph app
      handler
    end
  end

  tg-consumer -.- personal-assistant.tg.in
  tg-sender -.- personal-assistant.tg.out

  actor -.- telegram

  telegram -->|request| tg-consumer
  personal-assistant.tg.in --> handler --> personal-assistant.tg.out
  tg-sender -->|response| telegram
```
