import { Events } from 'discord.js';
import { handleInteractionError } from '../utils/errors/errorHandler.js';
import { CoolDownManager } from '../utils/cache/coolDown.js';

export default {
    name: Events.InteractionCreate,
    async execute(interaction) {
        const command = interaction.client.commands.get(interaction.commandName);
        if (!command) return;

        if (interaction.isAutocomplete()) {
            try {
                if (command.autocompleteHandler) {
                    return await command.autocompleteHandler(interaction);
                }
            } catch (error) {
                console.error('[Autocomplete Error]:', error);
                return await interaction.respond([]).catch(() => {});
            }
            return;
        }

        if (interaction.isChatInputCommand()) {
            const coolDownAmount = command.coolDown || 3;
            
            try {
                const { isLimited, timeLeft } = await CoolDownManager.check({
                        userId: interaction.user.id,
                        commandName: command.data.name,
                        coolDownSeconds: coolDownAmount,
                    });

                if (isLimited && timeLeft > 0) {
                    return await interaction.reply({
                        content: `⚠️ يرجى الانتظار **${timeLeft}** ثانية قبل استخدام أمر \`/${command.data.name}\` مجدداً.`,
                        ephemeral: true
                    });
                }
            } catch (redisError) {
                // console.error('[Redis Cooldown Error]:', redisError);
            }

            try {
                await command.execute(interaction);
            } catch (error) {
                console.error('[Command Execution Error]:', error);
                await handleInteractionError({ interaction, error });
            }
        }
    }
};