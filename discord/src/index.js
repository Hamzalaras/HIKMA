import { Client, GatewayIntentBits, Collection } from 'discord.js';
import 'dotenv/config';
import { commandHandler } from './handlers/command.handler.js';
import { eventHandler } from './handlers/event.handler.js';


const myBot = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

myBot.commands = new Collection();

await commandHandler(myBot);
await eventHandler(myBot);

process.on('unhandledRejection', (reason, promise) => {
    console.error('⚠️ [CRITICAL] Unhandled Rejection at:', promise, 'reason:', reason);
    //todo: dashboard
});

myBot.login(process.env.TOKEN);