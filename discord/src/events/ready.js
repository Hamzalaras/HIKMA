import { Events } from 'discord.js';

export default {
    once: true,
    name: Events.ClientReady,
    async execute() {
        try {
            console.log(`Ready ~~~ !`);
        } catch (error) {
            console.error(error);
        }
    }
};