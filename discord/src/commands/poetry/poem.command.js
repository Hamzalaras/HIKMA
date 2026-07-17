import { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { KATHER_ENDPOINTS, KATHER_ROUTES } from '../../constants/https.js';
import { getPoem, getPoemAutocomplete } from '../../services/poem.service.js';
import { buildPoemEmbed } from '../../utils/builders/embed.builders.js';
import { COMMAND_OPTIONS, CHOICES } from '../../constants/options.js';
import { withTimeout } from '../../utils/withTimeout.js';


const buildComponent = ({ line_count }) => [new ActionRowBuilder().addComponents(
                                new ButtonBuilder()
                                    .setCustomId('poem_more_hint')
                                    .setLabel(`💡 لقراءة باقي القصيدة ${line_count} إستخدم أمر /lines للأبيات الشعرية`)
                                    .setStyle(ButtonStyle.Secondary)
                                    .setDisabled(true)
                            )];

const data = new SlashCommandBuilder()
                .setName('قصيدة')
                .setDescription('الحصول على قصيدة')
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.POEM_ID)
                    .setDescription('إسم أو معرف القصيدة')
                    .setAutocomplete(true)
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.GENDER)
                    .setDescription('جنس الشاعر؛ ذكر أو أنثى')
                    .addChoices(
                        { name: CHOICES.GENDER.NAMES.MALE, value: CHOICES.GENDER.VALUES.MALE },
                        { name: CHOICES.GENDER.NAMES.FEMALE, value: CHOICES.GENDER.VALUES.FEMALE },
                    )
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.ERA)
                    .setDescription('إسم أو معرف العصر الذي عاش فيه الشاعر')
                    .setAutocomplete(true)
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.COUNTRY)
                    .setDescription('إسم أو معرف البلد الذي ولد فيه الشاعر')
                    .setAutocomplete(true)
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.POEM_TYPE)
                    .setDescription('نوع القصيدة')
                    .addChoices(
                        { name: CHOICES.POEM_TYPES.NAMES.AMUDI, value: CHOICES.POEM_TYPES.VALUES.AMUDI },
                        { name: CHOICES.POEM_TYPES.NAMES.PROSE, value: CHOICES.POEM_TYPES.VALUES.PROSE },
                        { name: CHOICES.POEM_TYPES.NAMES.TAFILA, value: CHOICES.POEM_TYPES.VALUES.TAFILA },
                        { name: CHOICES.POEM_TYPES.NAMES.FOREIGN, value: CHOICES.POEM_TYPES.VALUES.FOREIGN },
                    )
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.TOPIC)
                    .setDescription('موضوع القصيدة')
                    .setAutocomplete(true)
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.QUAFIA)
                    .setDescription('قافية القصيدة')
                    .setAutocomplete(true)
                )
                .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POEM.SEA)
                    .setDescription('بحر القصيدة')
                    .setAutocomplete(true)
                );

const execute = async (interaction) => {
    await interaction.deferReply();
    const userTag = `<@${interaction.user.id}>`;

    const [poem_id, gender, era, country, poemType, topic, quafia, sea] = [
        interaction.options.getString(COMMAND_OPTIONS.POEM.POEM_ID),
        interaction.options.getString(COMMAND_OPTIONS.POEM.GENDER),
        interaction.options.getString(COMMAND_OPTIONS.POEM.ERA),
        interaction.options.getString(COMMAND_OPTIONS.POEM.COUNTRY),
        interaction.options.getString(COMMAND_OPTIONS.POEM.POEM_TYPE),
        interaction.options.getString(COMMAND_OPTIONS.POEM.TOPIC),
        interaction.options.getString(COMMAND_OPTIONS.POEM.QUAFIA),
        interaction.options.getString(COMMAND_OPTIONS.POEM.SEA),
    ];

    const { poem, lines = [] } = await getPoem({ poem_id, gender, era, country, poemType, topic, quafia, sea });

    const embed = buildPoemEmbed({ poem, lines });

    const components = poem.line_count > lines.length ?
                        buildComponent({ line_count: poem.line_count }) : [];

    await interaction.editReply({
        content: userTag,
        embeds: [embed],
        components,
    });
    return;
};

const autocompleteHandler = async (interaction) => {
    const focusedOption = interaction.options.getFocused(true);
    const [optionName, optionValue] = [
        focusedOption.name,
        focusedOption.value.trim().toLowerCase(),
    ];

    const poem_id = interaction.options.getString(COMMAND_OPTIONS.POEM.POEM_ID);
    const options = {
        gender: interaction.options.getString(COMMAND_OPTIONS.POEM.GENDER),
        era: interaction.options.getString(COMMAND_OPTIONS.POEM.ERA),
        country: interaction.options.getString(COMMAND_OPTIONS.POEM.COUNTRY),
        poemType: interaction.options.getString(COMMAND_OPTIONS.POEM.POEM_TYPE),
        topic: interaction.options.getString(COMMAND_OPTIONS.POEM.TOPIC),
        quafia: interaction.options.getString(COMMAND_OPTIONS.POEM.QUAFIA),
        sea: interaction.options.getString(COMMAND_OPTIONS.POEM.SEA),
    };

    const choices = (optionName === COMMAND_OPTIONS.POEM.POEM_ID && 
                    Object.values(options).every(value => value == null))
                    || poem_id == null ?
                        await withTimeout({
                            fn: ({ signal }) => getPoemAutocomplete({ optionName, optionValue, signal }),
                            timeout: 2_700,
                        }) : 
                        [];

    await interaction.respond(choices.slice(0, 25));
    return;
};

export default { data, execute, autocompleteHandler };