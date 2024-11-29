// Copyright (c) Microsoft Corporation. All rights reserved.
// HelloAIAgent.cs

using Hello.Events;
using Microsoft.AutoGen.Abstractions;
using Microsoft.AutoGen.Core;
using Microsoft.Extensions.AI;

namespace HelloAIAgents;
[TopicSubscription("HelloAgents")]
public class HelloAIAgent(
    RuntimeContext context,
    [FromKeyedServices("EventTypes")] EventTypes typeRegistry,
    IHostApplicationLifetime hostApplicationLifetime,
    IChatClient client) : HelloAgent(
        context,
        typeRegistry,
        hostApplicationLifetime),
        IHandle<NewMessageReceived>
{
    // This Handle supercedes the one in the base class
    public async Task Handle(NewMessageReceived item)
    {
        var prompt = "Please write a limerick greeting someone with the name " + item.Message;
        var response = await client.CompleteAsync(prompt);
        var evt = new Output { Message = response.Message.Text };
        await PublishMessageAsync(evt).ConfigureAwait(false);

        var goodbye = new ConversationClosed { UserId = AgentId.Key, UserMessage = "Goodbye" };
        await PublishMessageAsync(goodbye).ConfigureAwait(false);
    }
}
