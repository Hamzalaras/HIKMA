
export class KatherBotError extends Error {
    constructor({ message, name, userFriendlyMessage }) {
        super(message);
        this.name = this.constructor.name;
        this.userFriendlyMessage = userFriendlyMessage || 'حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.';
        Error.captureStackTrace(this, this.constructor);
    }
}

export class ApiFetchError extends KatherBotError {
    constructor(message = 'API server is unavailable') {
        super({
            message,
            name: 'ApiFetchError',
            userFriendlyMessage: '🚨 عذراً، لم نتمكن من الاتصال بالخوادم حالياً. يرجى المحاولة لاحقاً.',
        });
    }
}

export class NotFoundError extends KatherBotError {
    constructor(message = 'Resource not found') {
        super({
            message,
            name: 'NotFoundError',
            userFriendlyMessage: '🔍 لم يتم العثور على بيانات مطابقة لبحثك.',
        });
    }
}