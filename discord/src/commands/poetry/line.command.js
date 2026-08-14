import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { getSingleLine, getSingleLineAutocomplete } from '../../services/lines.service.js';
import { COMMAND_OPTIONS, CHOICES } from '../../constants/options.js';
import { EMBED_COLORS, EMBED_FIELDS, UTIL_STRINGS } from '../../constants/embeds.js';
import { buildSingleLineEmbed } from '../../utils/builders/embed.builders.js';
import { withTimeout } from '../../utils/withTimeout.js';

const data = new SlashCommandBuilder()
    .setName('بيت')
    .setDescription('الحصول على بيت شعري واحد')
    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.LINE_ID)
        .setDescription('معرف البيت الشعري')
        .setAutocomplete(true))
    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.POEM)
        .setDescription('إستخراج بيت من قصيدة محددة (إسم أو معرف)')
        .setAutocomplete(true))
    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.LINE.POET)
        .setDescription('إستخراج بيت لشاعر محدد (إسم أو معرف)')
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

const execute = async (interaction) => {
    await interaction.deferReply();
    const userTag = `<@${interaction.user.id}>`;

    const options = {
        lineId: interaction.options.getString(COMMAND_OPTIONS.LINE.LINE_ID),
        poemId: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM),
        poetId: interaction.options.getString(COMMAND_OPTIONS.LINE.POET),
        lineType: interaction.options.getString(COMMAND_OPTIONS.LINE.LINE_TYPE),
        gender: interaction.options.getString(COMMAND_OPTIONS.LINE.GENDER),
        era: interaction.options.getString(COMMAND_OPTIONS.LINE.ERA),
        country: interaction.options.getString(COMMAND_OPTIONS.LINE.COUNTRY),
        poemType: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM_TYPE),
        topic: interaction.options.getString(COMMAND_OPTIONS.LINE.TOPIC),
        quafia: interaction.options.getString(COMMAND_OPTIONS.LINE.QUAFIA),
        sea: interaction.options.getString(COMMAND_OPTIONS.LINE.SEA),
    };

    const line = await getSingleLine(options);
    const embed = buildSingleLineEmbed(line);

    await interaction.editReply({
        content: userTag,
        embeds: [embed]
    });
};

const autocompleteHandler = async (interaction) => {
    const focusedOption = interaction.options.getFocused(true);
    const [optionName, optionValue] = [
        focusedOption.name,
        focusedOption.value.trim().toLowerCase(),
    ];

    const line_id = interaction.options.getString(COMMAND_OPTIONS.LINE.LINE_ID);

    const options = {
        poemId: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM),
        poetId: interaction.options.getString(COMMAND_OPTIONS.LINE.POET),
        lineType: interaction.options.getString(COMMAND_OPTIONS.LINE.LINE_TYPE),
        gender: interaction.options.getString(COMMAND_OPTIONS.LINE.GENDER),
        era: interaction.options.getString(COMMAND_OPTIONS.LINE.ERA),
        country: interaction.options.getString(COMMAND_OPTIONS.LINE.COUNTRY),
        poemType: interaction.options.getString(COMMAND_OPTIONS.LINE.POEM_TYPE),
        topic: interaction.options.getString(COMMAND_OPTIONS.LINE.TOPIC),
        quafia: interaction.options.getString(COMMAND_OPTIONS.LINE.QUAFIA),
        sea: interaction.options.getString(COMMAND_OPTIONS.LINE.SEA),
    };

    const choices = (optionName === COMMAND_OPTIONS.LINE.LINE_ID && 
                    Object.values(options).every(value => value == null)) 
                    || line_id == null ?
                        await withTimeout({
                            fn: ({ signal }) => getSingleLineAutocomplete({ optionName, optionValue, signal }),
                            timeout: 2_700,
                        }) :
                        [];


    await interaction.respond(choices.slice(0, 25));
};

export default {
    data, execute, autocompleteHandler,
    coolDown: 3,
};