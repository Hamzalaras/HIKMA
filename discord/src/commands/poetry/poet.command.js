import { SlashCommandBuilder } from 'discord.js';
import { KATHER_ENDPOINTS, KATHER_ROUTES } from '../../constants/https.js';
import { getPoet, getPoetAutocomplete } from '../../services/poet.service.js';
import { buildPoetEmbed } from '../../utils/builders/embed.builders.js';
import { CHOICES, COMMAND_OPTIONS } from '../../constants/options.js';
import { withTimeout } from '../../utils/withTimeout.js';

const data = new SlashCommandBuilder()
                    .setName('شاعر')
                    .setDescription('الحصول على شاعر')
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POET.POET_ID)
                                               .setDescription('إسم أو معرف الشاعر')
                                               .setAutocomplete(true)
                                            )
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POET.GENDER)
                                               .setDescription('جنس الشاعر؛ ذكر أو أنثى')
                                               .addChoices(
                                                   { name: CHOICES.GENDER.NAMES.MALE, value: CHOICES.GENDER.VALUES.MALE },
                                                   { name: CHOICES.GENDER.NAMES.FEMALE, value: CHOICES.GENDER.VALUES.FEMALE },
                                               )
                                            )
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POET.ERA)
                                               .setDescription('إسم أو معرف العصر الذي عاش فيه الشاعر')
                                               .setAutocomplete(true)
                                            )
                    .addStringOption(opt => opt.setName(COMMAND_OPTIONS.POET.COUNTRY)
                                               .setDescription('إسم أو معرف البلد الذي ولد فيه الشاعر')
                                               .setAutocomplete(true)
                                            );

const execute = async (interaction) => {
    await interaction.deferReply();
    const userTag = `<@${interaction.user.id}>`;
    const [poetId, gender, era, country] = 
        [
            interaction.options.getString(COMMAND_OPTIONS.POET.POET_ID),
            interaction.options.getString(COMMAND_OPTIONS.POET.GENDER),
            interaction.options.getString(COMMAND_OPTIONS.POET.ERA),
            interaction.options.getString(COMMAND_OPTIONS.POET.COUNTRY),
        ];
    const poet = await getPoet({ poetId, gender, era, country });
    
    const embed = buildPoetEmbed({ poet });

    await interaction.editReply({
        content: userTag,
        embeds: [embed]
    });
    return;
};

const autocompleteHandler = async (interaction) => {
    const focusedOption = interaction.options.getFocused(true);
    const [optionName, optionValue] = 
        [
            focusedOption.name,
            focusedOption.value.trim().toLowerCase()
        ];

    const poetId = interaction.options.getString(COMMAND_OPTIONS.POET.POET_ID);
    const options = {
            gender: interaction.options.getString(COMMAND_OPTIONS.POET.GENDER),
            era: interaction.options.getString(COMMAND_OPTIONS.POET.ERA),
            country: interaction.options.getString(COMMAND_OPTIONS.POET.COUNTRY),
        }
    const choices = (optionName === COMMAND_OPTIONS.POET.POET_ID && 
                    Object.values(options).every(value => value == null)) 
                    || poetId == null ?
                        await withTimeout({
                            fn: ({ signal }) => getPoetAutocomplete({ optionName, optionValue, signal }),
                            timeout: 2_700,
                        }) :
                        [];

    await interaction.respond(choices.slice(0, 25));
    return;
};

export default { data, execute, autocompleteHandler };