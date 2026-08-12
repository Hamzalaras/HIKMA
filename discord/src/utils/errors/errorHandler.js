import { KatherBotError } from './Errors.js';
import { buildErrorEmbed } from '../builders/embed.builders.js';


export const handleInteractionError = async ({ interaction, error }) => {
    console.error(`[${error.name || 'Error'}]:`, error.message);
    
    const errorEmbed = buildErrorEmbed({ error });

    if (process.env.OWNER_ID && process.env.MODE !== 'DEV') {
        try {
            const developer = await interaction.client.users.fetch(process.env.OWNER_ID);

            const stackTrace = error.stack ? error.stack.split('\n').slice(0, 4).join(' -> ') : error.message;
            const cleanDetails = String(stackTrace).replace(/\\n|\n/g, " ").slice(0, 1500);
            const dmContent = "🚨 Alert | User: <@" + interaction.user.id + "> | Command: " + (interaction.commandName || "Unknown") + " | Stack: " + cleanDetails;
            
            await developer.send({
                content: dmContent,
                embeds: [errorEmbed]
            });
        } catch (dmError) {
            console.error('Failed to send error DM:', dmError.message);
        }        
    }

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