import { Events } from 'discord.js';
import { PREFIX } from '../constants/prefixes.js';

export default {
    name: Events.MessageCreate,
    async execute(message) {
        if (message.author.bot || !message.content.startsWith(PREFIX)) return;
        if (message.author.id !== process.env.OWNER_ID) return;

        const args = message.content.slice(PREFIX.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        const command = message.client.commands?.get(commandName);
        if (!command) return;

        try {
            await command.execute({ message, args });
        } catch (error) {
            console.error(`[Message Command Error] [${commandName}]:`, error);
        }
    }
};