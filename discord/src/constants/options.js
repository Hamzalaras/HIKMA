

const BASIC_OPTIONS = {
    GENDER: 'الجنس',
    ERA: 'عصر',
    COUNTRY: 'بلد',
};

const POEM_OPTIONS = {
    POEM_TYPE: 'نوع_القصيدة',
    TOPIC: 'موضوع',
    QUAFIA: 'قافية',
    SEA: 'بحر',
};

export const COMMAND_OPTIONS = {
    POET: {
        POET_ID: 'معرف',
        ...BASIC_OPTIONS,
    },
    POEM: {
        POEM_ID: 'معرف',
        ...BASIC_OPTIONS,
        ...POEM_OPTIONS,
    },
    LINE: {
        LINE_ID: 'معرف',
        ...BASIC_OPTIONS,
        ...POEM_OPTIONS,
        LINE_TYPE: 'نوع_البيت',
        POEM: 'القصيدة',
        POET: 'الشاعر',
    },
};

export const CHOICES = {
    GENDER: {
        NAMES: {
            MALE: 'ذكر',
            FEMALE: 'أنثى',
        },
        VALUES: {
            MALE: 'male',
            FEMALE: 'female',
        },
    },
    POEM_TYPES: {
        NAMES: {
            AMUDI: 'عمودية',
            PROSE: 'نثرية',
            TAFILA: 'تفعيلة',
            FOREIGN: 'مترجمة',
        },
        VALUES: {
            AMUDI: '1',
            PROSE: '2',
            TAFILA: '3',
            FOREIGN: '4',
        },
    },
    LINE_TYPES: {
        NAMES: {
            NULL: 'فارغ',
            SADR: 'صدر',
            AJZ: 'عجز',
            FREE_VERSE: 'حر',
        },
        VALUES: {
            NULL: '0',
            SADR: '1',
            AJZ: '2',
            FREE_VERSE: '3',
        },

    },
};