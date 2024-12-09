from enum import Enum, auto
from sqlglot.tokens import TokenType as GlotType
from . import tokenizer

class _TokTypeGroup(Enum):
    # SemiColon = auto() # goes into keyword
    EmbededVariableStart = auto()
    Number = auto()
    IdentifierOrTrash = auto() # Identifier Or Trash
    String = auto()
    Type = auto() # DataType
    Keyword = auto() # Keyword or SemiColon
    Other = auto()
    Comment = auto()

_group_type_by_glot_type: dict[GlotType, _TokTypeGroup] = {} # init in _setup_dict


def get_group_name(glotType: GlotType) -> str:
    _setup_dict()
    return _group_type_by_glot_type[glotType].name #.lower()

def token_type_names() -> list[str]: 
    return [name for name, type in _TokTypeGroup.__members__.items()]

def fake_glot_type_comment(): return -1


def _setup_dict():
    if _group_type_by_glot_type != {}:
        return
    _group_set_by_grouptype: dict[_TokTypeGroup, GlotType] = {}

    _group_set_by_grouptype[_TokTypeGroup.Comment] = {fake_glot_type_comment()} # there is no glotToken for comments
    # _group_set_by_grouptype[_TokTypeGroup.SemiColon] = {GlotType.SEMICOLON}
    _group_set_by_grouptype[_TokTypeGroup.EmbededVariableStart] = {GlotType.COLON}
    _group_set_by_grouptype[_TokTypeGroup.Number] = {GlotType.NUMBER}

    _group_set_by_grouptype[_TokTypeGroup.IdentifierOrTrash] = {
        GlotType.IDENTIFIER,
        GlotType.VAR,
        GlotType.PARAMETER,
    }

    _group_set_by_grouptype[_TokTypeGroup.String] = { # string tokens are also listed in the insert parser
        GlotType.BIT_STRING,
        GlotType.HEX_STRING,
        GlotType.BYTE_STRING,
        GlotType.NATIONAL_STRING,
        GlotType.RAW_STRING,
        GlotType.HEREDOC_STRING,
        GlotType.UNICODE_STRING,
        GlotType.STRING,
    }

    _group_set_by_grouptype[_TokTypeGroup.Type] = {
        GlotType.BIT,
        GlotType.BOOLEAN,
        GlotType.TINYINT,
        GlotType.UTINYINT,
        GlotType.SMALLINT,
        GlotType.USMALLINT,
        GlotType.MEDIUMINT,
        GlotType.UMEDIUMINT,
        GlotType.INT,
        GlotType.UINT,
        GlotType.BIGINT,
        GlotType.UBIGINT,
        GlotType.INT128,
        GlotType.UINT128,
        GlotType.INT256,
        GlotType.UINT256,
        GlotType.FLOAT,
        GlotType.DOUBLE,
        GlotType.DECIMAL,
        GlotType.DECIMAL32,
        GlotType.DECIMAL64,
        GlotType.DECIMAL128,
        GlotType.UDECIMAL,
        GlotType.BIGDECIMAL,
        GlotType.CHAR,
        GlotType.NCHAR,
        GlotType.VARCHAR,
        GlotType.NVARCHAR,
        GlotType.BPCHAR,
        GlotType.TEXT,
        GlotType.MEDIUMTEXT,
        GlotType.LONGTEXT,
        GlotType.MEDIUMBLOB,
        GlotType.LONGBLOB,
        GlotType.TINYBLOB,
        GlotType.TINYTEXT,
        GlotType.NAME,
        GlotType.BINARY,
        GlotType.VARBINARY,
        GlotType.JSON,
        GlotType.JSONB,
        GlotType.TIME,
        GlotType.TIMETZ,
        GlotType.TIMESTAMP,
        GlotType.TIMESTAMPTZ,
        GlotType.TIMESTAMPLTZ,
        GlotType.TIMESTAMPNTZ,
        GlotType.TIMESTAMP_S,
        GlotType.TIMESTAMP_MS,
        GlotType.TIMESTAMP_NS,
        GlotType.DATETIME,
        GlotType.DATETIME64,
        GlotType.DATE,
        GlotType.DATE32,
        GlotType.INT4RANGE,
        GlotType.INT4MULTIRANGE,
        GlotType.INT8RANGE,
        GlotType.INT8MULTIRANGE,
        GlotType.NUMRANGE,
        GlotType.NUMMULTIRANGE,
        GlotType.TSRANGE,
        GlotType.TSMULTIRANGE,
        GlotType.TSTZRANGE,
        GlotType.TSTZMULTIRANGE,
        GlotType.DATERANGE,
        GlotType.DATEMULTIRANGE,
        GlotType.UUID,
        GlotType.GEOGRAPHY,
        GlotType.NULLABLE,
        GlotType.GEOMETRY,
        GlotType.HLLSKETCH,
        GlotType.HSTORE,
        GlotType.SUPER,
        GlotType.SERIAL,
        GlotType.SMALLSERIAL,
        GlotType.BIGSERIAL,
        GlotType.XML,
        GlotType.YEAR,
        GlotType.UNIQUEIDENTIFIER,
        GlotType.USERDEFINED,
        GlotType.MONEY,
        GlotType.SMALLMONEY,
        GlotType.ROWVERSION,
        GlotType.IMAGE,
        GlotType.VARIANT,
        GlotType.OBJECT,
        GlotType.INET,
        GlotType.IPADDRESS,
        GlotType.IPPREFIX,
        GlotType.IPV4,
        GlotType.IPV6,
        GlotType.ENUM,
        GlotType.ENUM8,
        GlotType.ENUM16,
        GlotType.FIXEDSTRING,
        GlotType.LOWCARDINALITY,
        GlotType.NESTED,
        GlotType.AGGREGATEFUNCTION,
        GlotType.SIMPLEAGGREGATEFUNCTION,
        GlotType.TDIGEST,
        GlotType.UNKNOWN,
        GlotType.VECTOR,
    }

    _group_set_by_grouptype[_TokTypeGroup.Keyword] = {GlotType.SEMICOLON}.union(tokenizer.keywords())

    _group_set_by_grouptype[_TokTypeGroup.Other] = {
        GlotType.L_PAREN,
        GlotType.R_PAREN,
        GlotType.L_BRACKET,
        GlotType.R_BRACKET,
        GlotType.L_BRACE,
        GlotType.R_BRACE,
        GlotType.COMMA,
        GlotType.DOT,
        GlotType.DASH,
        GlotType.PLUS,
        GlotType.DCOLON,
        GlotType.DQMARK,
        GlotType.STAR,
        GlotType.BACKSLASH,
        GlotType.SLASH,
        GlotType.LT,
        GlotType.LTE,
        GlotType.GT,
        GlotType.GTE,
        GlotType.NOT,
        GlotType.EQ,
        GlotType.NEQ,
        GlotType.NULLSAFE_EQ,
        GlotType.COLON_EQ,
        GlotType.AMP,
        GlotType.DPIPE,
        GlotType.PIPE,
        GlotType.PIPE_SLASH,
        GlotType.DPIPE_SLASH,
        GlotType.CARET,
        GlotType.TILDA,
        GlotType.ARROW,
        GlotType.DARROW,
        GlotType.FARROW,
        GlotType.HASH,
        GlotType.HASH_ARROW,
        GlotType.DHASH_ARROW,
        GlotType.LR_ARROW,
        GlotType.DAT,
        GlotType.LT_AT,
        GlotType.AT_GT,
        GlotType.DOLLAR,
        GlotType.SESSION_PARAMETER,
        GlotType.DAMP,
        GlotType.DSTAR,
        GlotType.BLOCK_END,
    }


    # _group_type_by_glot_type: dict[GlotType, _TokTypeGroup] = {}
    for groupType, groupSet in _group_set_by_grouptype.items():
        for glotType in groupSet:
            _group_type_by_glot_type[glotType] = groupType


