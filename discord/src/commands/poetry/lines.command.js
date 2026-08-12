import { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ComponentType } from 'discord.js';
import { getLines, getLinesAutocomplete } from '../../services/lines.service.js';
import { buildLinesEmbed } from '../../utils/builders/embed.builders.js';
import { COMMAND_OPTIONS, CHOICES } from '../../constants/options.js';
import { withTimeout } from '../../utils/withTimeout.js';

const data = new SlashCommandBuilder()
                    .setName('أبيات')
                    .setDescription('الحصول على أبيات شعرية')
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.POEM)
                        .setDescription('إستخراج أبيات من قصيدة محددة (إسم أو معرف)')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.POET)
                        .setDescription('إستخراج أبيات لشاعر محدد (إسم أو معرف)')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.LINE_TYPE)
                        .setDescription('نوع البيت (صدر، عجز، حر)')
                        .addChoices(
                            { name: CHOICES.LINE_TYPES.NAMES.SADR, value: CHOICES.LINE_TYPES.VALUES.SADR },
                            { name: CHOICES.LINE_TYPES.NAMES.AJZ, value: CHOICES.LINE_TYPES.VALUES.AJZ },
                            { name: CHOICES.LINE_TYPES.NAMES.FREE_VERSE, value: CHOICES.LINE_TYPES.VALUES.FREE_VERSE },
                        ))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.GENDER)
                        .setDescription('جنس الشاعر؛ ذكر أو أنثى')
                        .addChoices(
                            { name: CHOICES.GENDER.NAMES.MALE, value: CHOICES.GENDER.VALUES.MALE },
                            { name: CHOICES.GENDER.NAMES.FEMALE, value: CHOICES.GENDER.VALUES.FEMALE },
                        ))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.ERA)
                        .setDescription('إسم أو معرف العصر الذي عاش فيه الشاعر')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.COUNTRY)
                        .setDescription('إسم أو معرف البلد الذي ولد فيه الشاعر')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.POEM_TYPE)
                        .setDescription('نوع القصيدة')
                        .addChoices(
                            { name: CHOICES.POEM_TYPES.NAMES.AMUDI, value: CHOICES.POEM_TYPES.VALUES.AMUDI },
                            { name: CHOICES.POEM_TYPES.NAMES.PROSE, value: CHOICES.POEM_TYPES.VALUES.PROSE },
                            { name: CHOICES.POEM_TYPES.NAMES.TAFILA, value: CHOICES.POEM_TYPES.VALUES.TAFILA },
                            { name: CHOICES.POEM_TYPES.NAMES.FOREIGN, value: CHOICES.POEM_TYPES.VALUES.FOREIGN },
                        ))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.TOPIC)
                        .setDescription('موضوع القصيدة')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.QUAFIA)
                        .setDescription('قافية القصيدة')
                        .setAutocomplete(true))
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.SEA)
                        .setDescription('بحر القصيدة')
                        .setAutocomplete(true));

const buildPaginationRow = (currentEmbedPage, totalPages) => {
    return new ActionRowBuilder().addComponents(
        new ButtonBuilder()
            .setCustomId('lines_prev')
            .setLabel('السابق')
            .setStyle(ButtonStyle.Primary)
            .setDisabled(currentEmbedPage <= 1),
        new ButtonBuilder()
            .setCustomId('lines_next')
            .setLabel('التالي')
            .setStyle(ButtonStyle.Primary)
            .setDisabled(currentEmbedPage >= totalPages)
    );
};

const execute = async (interaction) => {
    await interaction.deferReply();
    const userTag = `<@${interaction.user.id}>`;

    const options = {
        poem: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM),
        poet: interaction.options.getString(COMMAND_OPTIONS.LINE.POET),
        lineType: interaction.options.getString(COMMAND_OPTIONS.LINE.LINE_TYPE),
        gender: interaction.options.getString(COMMAND_OPTIONS.LINE.GENDER),
        era: interaction.options.getString(COMMAND_OPTIONS.LINE.ERA),
        country: interaction.options.getString(COMMAND_OPTIONS.LINE.COUNTRY),
        poemType: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM_TYPE),
        topic: interaction.options.getString(COMMAND_OPTIONS.LINE.TOPIC),
        quafia: interaction.options.getString(COMMAND_OPTIONS.LINE.QUAFIA),
        sea: interaction.options.getString(COMMAND_OPTIONS.LINE.SEA),
    };

    const linesPerPage = 6;
    const apiLimit = 50;
    
    let currentEmbedPage = 1;
    let apiPage = 1;

    let response = await getLines({ ...options, page: apiPage, limit: apiLimit });
    
    let cachedLines = response.data || [];
    let hasMoreApi = response.pagination?.has_more || false;
    let totalLines = response.pagination?.total || cachedLines.length;

    const getTotalEmbedPages = () => Math.ceil(totalLines / linesPerPage);

    const getSlice = () => {
        const start = (currentEmbedPage - 1) * linesPerPage;
        const end = start + linesPerPage;
        return cachedLines.slice(start, end);
    };

    const buildCurrentEmbed = () => {
        return buildLinesEmbed({ 
            response: { 
                data: getSlice(), 
                poem: response.poem, 
                poet: response.poet, 
                pagination: { 
                    page: currentEmbedPage, 
                    total_pages: getTotalEmbedPages() 
                } 
            } 
        });
    };

    const embed = buildCurrentEmbed();
    const totalPages = getTotalEmbedPages();
    const components = totalPages > 1 ? [buildPaginationRow(currentEmbedPage, totalPages)] : [];

    const message = await interaction.editReply({
        content: userTag,
        embeds: [embed],
        components,
    });

    if (components.length > 0) {
        const collector = message.createMessageComponentCollector({
            componentType: ComponentType.Button,
            time: 300_000, 
        });

        collector.on('collect', async (i) => {
            if (i.user.id !== interaction.user.id) {
                await i.reply({ content: 'لا يمكنك استخدام هذه الأزرار.', ephemeral: true });
                return;
            }

            if (i.customId === 'lines_next') currentEmbedPage += 1;
            if (i.customId === 'lines_prev') currentEmbedPage -= 1;

            await i.deferUpdate();

            if (currentEmbedPage * linesPerPage > cachedLines.length && hasMoreApi) {
                apiPage += 1;
                const newResponse = await getLines({ ...options, page: apiPage, limit: apiLimit });
                cachedLines.push(...(newResponse.data || []));
                hasMoreApi = newResponse.pagination?.has_more || false;
                totalLines = newResponse.pagination?.total || totalLines;
            }

            await i.editReply({
                embeds: [buildCurrentEmbed()],
                components: [buildPaginationRow(currentEmbedPage, getTotalEmbedPages())],
            });
        });

        collector.on('end', async () => {
            try {
                const currentMessage = await interaction.fetchReply();
                if (!currentMessage.components || currentMessage.components.length === 0) return;

                const disabledComponents = currentMessage.components.map(row => {
                    const builder = ActionRowBuilder.from(row);
                    builder.components.forEach(button => {
                        button.setDisabled(true);
                    });
                    return builder;
                });

                await interaction.editReply({
                    components: disabledComponents,
                });
            } catch (error) {
            }
        });
    }
};

const autocompleteHandler = async (interaction) => {
    const focusedOption = interaction.options.getFocused(true);
    const [optionName, optionValue] = [
        focusedOption.name,
        focusedOption.value.trim().toLowerCase(),
    ];

    const choices = await withTimeout({
        fn: ({ signal }) => getLinesAutocomplete({ optionName, optionValue, signal }),
        timeout: 2_700,
    });
    await interaction.respond(choices.slice(0, 25));
};

export default { data, execute, autocompleteHandler };