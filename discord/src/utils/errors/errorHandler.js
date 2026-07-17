import { KatherBotError } from './Errors.js';
import { buildErrorEmbed } from '../builders/embed.builders.js';


export const handleInteractionError = async ({ interaction, error }) => {
    console.error(`[${error.name || 'Error'}]:`, error.message);
    
    const errorEmbed = buildErrorEmbed({ error });

    try {
        if (interaction.deferred || interaction.replied) {
            await interaction.editReply({ content: `<@${interaction.user.id}>`, embeds: [errorEmbed] });
        } else {
            await interaction.reply({ embeds: [errorEmbed], ephemeral: true });
        }
    } catch (fallbackError) {
        console.error('Failed to send error message to Discord:', fallbackError.message);
    }
};