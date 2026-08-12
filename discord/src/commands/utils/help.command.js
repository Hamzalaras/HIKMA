import { SlashCommandBuilder } from 'discord.js';
import { buildHelpEmbed } from '../../utils/builders/embed.builders.js';

const data = new SlashCommandBuilder()
    .setName('مساعدة')
    .setDescription('عرض قائمة الأوامر وشرح كيفية استخدام فلاتر البحث في البوت');

const execute = async (interaction) => {
    const embed = buildHelpEmbed();

    await interaction.reply({
        embeds: [embed],
        ephemeral: true
    });
};

export default { data, execute };