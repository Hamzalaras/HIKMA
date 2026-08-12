import { EmbedBuilder } from 'discord.js';
import { EMBED_COLORS, EMBED_FIELDS, UTIL_STRINGS } from '../../constants/embeds.js';
import { CHOICES } from '../../constants/options.js';
import { KatherBotError } from '../errors/Errors.js';
import { HELP_CONTENT } from '../../constants/helpContent.js';

export const buildPoetEmbed = ({ poet }) => {

    let biography = poet.bio || UTIL_STRINGS.NO_BIO;
    if (biography.length > 800) {
        biography = biography.substring(0, 500) + UTIL_STRINGS.READ_MORE;
    }
    const gender = poet.gender ?
                        poet.gender === CHOICES.GENDER.VALUES.MALE ? 
                            CHOICES.GENDER.NAMES.MALE : 
                            CHOICES.GENDER.NAMES.FEMALE : 
                        UTIL_STRINGS.UNKNOWN;
    const country = poet.country?.name_ar || UTIL_STRINGS.UNKNOWN;
    const era = poet.era?.name_ar || UTIL_STRINGS.UNKNOWN;
    const embed = new EmbedBuilder()
        .setColor(EMBED_COLORS.CAMEL)
        .setTitle(`${EMBED_FIELDS.POET}: ${poet.name_ar}`)
        .setDescription(biography)
        .addFields(
            { name: EMBED_FIELDS.ID, value: `${poet.id}`, inline: true },
            { name: EMBED_FIELDS.GENDER, value: gender, inline: true },
            { name: EMBED_FIELDS.COUNTRY, value: country, inline: true },
            { name: EMBED_FIELDS.ERA, value: era, inline: true }
        )
        .setFooter({ text: UTIL_STRINGS.EXTRACTED_KATHER })
        .setTimestamp();

    return embed;
};

export const buildPoemEmbed = ({ poem, lines = [] }) => {
    let description = lines.map(line => line.content).filter(Boolean).join('\n'); 
    if (!description.length) description = UTIL_STRINGS.UNKNOWN;

    if (description.length > 1024) {
        description = description.substring(0, 1000) + '...';
    }
 
    const poetName = poem.poet?.name_ar || UTIL_STRINGS.UNKNOWN;
    const gender = poem.poet?.gender ?
                        poem.poet?.gender === CHOICES.GENDER.VALUES.MALE ?
                            CHOICES.GENDER.NAMES.MALE :
                            CHOICES.GENDER.NAMES.FEMALE :
                        UTIL_STRINGS.UNKNOWN;
    const country = poem.poet?.country?.name_ar || UTIL_STRINGS.UNKNOWN;
    const era = poem.poet?.era?.name_ar || UTIL_STRINGS.UNKNOWN;
    const topic = poem.topic?.name_ar || UTIL_STRINGS.UNKNOWN;
    const sea = poem.sea?.name_ar || UTIL_STRINGS.UNKNOWN;
    const quafia = poem.quafia?.name_ar || UTIL_STRINGS.UNKNOWN;
    const poemType = poem.type?.name_ar || UTIL_STRINGS.UNKNOWN;
    
    const embed = new EmbedBuilder()
        .setColor(EMBED_COLORS.CAMEL)
        .setTitle(`${EMBED_FIELDS.POEM}: ${poem.name}`)
        .setDescription(description)
        .addFields(
            { name: EMBED_FIELDS.ID, value: `${poem.id}`, inline: true },
            { name: EMBED_FIELDS.POET, value: poetName, inline: true },
            { name: EMBED_FIELDS.GENDER, value: gender, inline: true },
            { name: EMBED_FIELDS.COUNTRY, value: country, inline: true },
            { name: EMBED_FIELDS.ERA, value: era, inline: true },
            { name: EMBED_FIELDS.SEA, value: sea, inline: true },
            { name: EMBED_FIELDS.TOPIC, value: topic, inline: true },
            { name: EMBED_FIELDS.QUAFIA, value: quafia, inline: true },
            { name: EMBED_FIELDS.POEM_TYPE, value: poemType, inline: true },
        );
 
    embed.setFooter({ text: UTIL_STRINGS.EXTRACTED_KATHER })
        .setTimestamp();
 
    return embed;
};

export const buildLinesEmbed = ({ response }) => {
    const { data = [], poem, poet, pagination } = response;

    let description = data.map(line => line.content).filter(Boolean).join('\n\n');
    if (!description.length) description = UTIL_STRINGS.UNKNOWN;

    if (description.length > 4000) {
        description = description.substring(0, 3995) + '...';
    }

    const embed = new EmbedBuilder()
        .setColor(EMBED_COLORS.CAMEL)
        .setDescription(`**${description}**`);

    let title = EMBED_FIELDS.LINES;
    
    if (poem) {
        title += ` من قصيدة: ${poem.name}`;
        const poetName = poem.poet?.name_ar || UTIL_STRINGS.UNKNOWN;
        embed.addFields(
            { name: EMBED_FIELDS.POEM, value: poem.name, inline: true },
            { name: EMBED_FIELDS.POET, value: poetName, inline: true }
        );
    } else if (poet) {
        title += ` للشاعر: ${poet.name_ar}`;
        const eraName = poet.era?.name_ar || UTIL_STRINGS.UNKNOWN;
        embed.addFields(
            { name: EMBED_FIELDS.POET, value: poet.name_ar, inline: true },
            { name: EMBED_FIELDS.ERA, value: eraName, inline: true }
        );
    } else {
        embed.setTitle(title);
    }

    embed.setTitle(title.length > 256 ? title.substring(0, 253) + '...' : title);

    const footerText = pagination 
        ? `${UTIL_STRINGS.EXTRACTED_KATHER} • صفحة ${pagination.page} من ${pagination.total_pages}`
        : UTIL_STRINGS.EXTRACTED_KATHER;
    
    embed.setFooter({ text: footerText }).setTimestamp();

    return embed;
};

export const buildSingleLineEmbed = (line) => {
    const poem = line.poem || {};
    const poet = poem.poet || {};

    const content = line.content || UTIL_STRINGS.UNKNOWN;
    const poetName = poet.name_ar || UTIL_STRINGS.UNKNOWN;
    const poemName = poem.name || UTIL_STRINGS.UNKNOWN;
    
    const gender = poet.gender ?
                        poet.gender === CHOICES.GENDER.VALUES.MALE ? 
                            CHOICES.GENDER.NAMES.MALE : 
                            CHOICES.GENDER.NAMES.FEMALE : 
                        UTIL_STRINGS.UNKNOWN;
    const country = poet.country?.name_ar || UTIL_STRINGS.UNKNOWN;
    const era = poet.era?.name_ar || UTIL_STRINGS.UNKNOWN;
    const topic = poem.topic?.name_ar || UTIL_STRINGS.UNKNOWN;
    const sea = poem.sea?.name_ar || UTIL_STRINGS.UNKNOWN;
    const quafia = poem.quafia?.name_ar || UTIL_STRINGS.UNKNOWN;
    const poemType = poem.type?.name_ar || UTIL_STRINGS.UNKNOWN;

    const embed = new EmbedBuilder()
        .setColor(EMBED_COLORS.CAMEL)
        .setTitle(EMBED_FIELDS.LINE)
        .setDescription(`**${content}**`)
        .addFields(
            { name: EMBED_FIELDS.ID, value: `${line.id}`, inline: true },
            { name: EMBED_FIELDS.POET, value: poetName, inline: true },
            { name: EMBED_FIELDS.POEM, value: poemName, inline: true },
            { name: EMBED_FIELDS.GENDER, value: gender, inline: true },
            { name: EMBED_FIELDS.COUNTRY, value: country, inline: true },
            { name: EMBED_FIELDS.ERA, value: era, inline: true },
            { name: EMBED_FIELDS.SEA, value: sea, inline: true },
            { name: EMBED_FIELDS.TOPIC, value: topic, inline: true },
            { name: EMBED_FIELDS.QUAFIA, value: quafia, inline: true },
            { name: EMBED_FIELDS.POEM_TYPE, value: poemType, inline: true }
        )
        .setFooter({ text: UTIL_STRINGS.EXTRACTED_KATHER })
        .setTimestamp();

    return embed;
};

export const buildHelpEmbed = () => {
    const embed = new EmbedBuilder()
        .setColor(EMBED_COLORS.CAMEL)
        .setTitle(HELP_CONTENT.general.title)
        .setDescription(`${HELP_CONTENT.general.description}\n\n${HELP_CONTENT.tips}`)
        .setFooter({ text: UTIL_STRINGS.EXTRACTED_KATHER });

    const commandFields = Object.values(HELP_CONTENT.commands).map(cmd => ({
        name: `/${cmd.name}`,
        value: `**الوصف:** ${cmd.description}\n**الخيارات المتاحة:**\n${cmd.options}`,
        inline: false
    }));

    embed.addFields(commandFields);

    return embed;
};

export const buildErrorEmbed = ({ error }) => {
    const description = error instanceof KatherBotError 
        ? error.userFriendlyMessage 
        : 'حدث خطأ داخلي في الخادم. الرجاء إبلاغ المطور.';

    return new EmbedBuilder()
        .setColor('#E74C3C')
        .setTitle('❌ حدث خطأ')
        .setDescription(description)
        .setTimestamp();
};