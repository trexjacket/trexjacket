import datetime as dt
import re

from .utils import clean_record_key


class Field:
    """Represents a dimension of a selected Mark"""

    def __init__(self, name, value):
        self._value = None
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Dimension(name={self.name!r}, value={self.value!r})"

    def __hash__(self):
        return hash((self.name, self.value))

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    @property
    def serialized(self):
        return {"name": self.name, "value": self.value}

    @property
    def value(self):
        """Property that returns the Class value"""
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value for the Class

        Parameters
        ----------
        value
        """
        try:
            iso_string = value.toISOString().replace("Z", "+00:00")
            self._value = dt.datetime.fromisoformat(iso_string)
        except AttributeError:
            self._value = value


class Measure(Field):
    pass


class Dimensions(dict):
    def __init__(self, frozen_fields):
        self.fields = frozen_fields
        super().__init__(**{f.name: f.value for f in self.fields})

    def __hash__(self):
        return hash(self.fields)

    def __eq__(self, other):
        return self.fields == other.fields

    def __setitem__(self, value):
        raise KeyError("Can't update mark dimensions.")

    def __dict__(self):
        return {f.name: f.value for f in self.fields}


class Mark:
    """A class to represent a selected mark on a worksheet

    Attributes
    ----------
    dimension : Dimensions
        representation of the identifying dimensions
    identifier : tuple
        dimension values identifying the mark
    measures : tuple
        of the underlying data
    values : tuple
        of the actual data that is associated with this mark
        mapped to measures

    Marks are accessible by case-insensitive dictionary lookup
    i.e. a mark can be accessed mark['profit'] and this will return the value
    associated with any of:
      mark measure SUM(Profit)
      mark measure (Profit)
    """

    def __init__(self, dimension):
        """Class initialization"""
        self.values_dict = dict()
        self.dimension = dimension

    def __str__(self):
        """Representation of the Class object as a string"""
        return f"Mark: Identified by {self.dimension}, values: {self.values_dict}"

    def __repr__(self):
        return str(self)

    def _to_dict(self):
        """Representation of the Class object as a dict"""
        return {
            "dimension": dict(self.dimension),
            "measures": self.measures,
            "values": list(self._values.values()),
        }

    @property
    def identifier(self):
        """Property that returns the dimension values of the Class"""
        return list(self.dimension.values())

    @property
    def identifying_properties(self):
        """Property that returns the names of each dimension"""
        return (d.name for d in self.dimension)

    @property
    def values(self):
        """Property that returns the Class values"""
        return self.values_dict

    @property
    def measures(self):
        """Property that returns the Class measures"""
        return list(self.values_dict.keys())

    def __getitem__(self, key):
        """Getter method for improved readability

        Parameters
        ----------
        key
        """
        return self.values_dict[clean_record_key(key)]

    def get(self, key):
        """Getter method for improved readability

        Parameters
        ----------
        key
        """
        return self.values_dict.get(clean_record_key(key))


aggregation_pattern = re.compile(r"(^agg|sum|AGG|SUM)\((.*)\)$")
datetime_pattern = re.compile(r"(^month)\((.*)\)$")


def build_marks(records):
    """Generates Marks

    we iterate through all records.
    Some "Marks" can be assembled from multiple records if they share a common
    identifier (frozen set of dimensions)
    This is not really known until we have iterated through all records
    We do rely on a record having a complete set of dimensions, or they will be
    assembled separately (i.e. dimensions
    must fully overlap for us to group them)
    """
    marks = dict()
    for record in records:
        all_dimensions = set()
        all_values = dict()
        measure_flag = False
        measure_name = None
        measure_value = None
        for key, value in record.items():
            this_value = None
            this_dimension = None
            aggregation_match = aggregation_pattern.search(key)
            datetime_match = datetime_pattern.search(key)
            category_match = isinstance(value, str)
            is_measure_name = key == "Measure Names"
            is_measure_value = key == "Measure Values"

            if is_measure_name:
                measure_flag = True
                measure_name = value

            elif is_measure_value:
                measure_flag = True
                measure_value = value

            elif datetime_match:
                name = datetime_match.group(2)
                this_dimension = Field(name, value)

            elif category_match:
                this_dimension = Field(key, value)

            elif aggregation_match:
                name = aggregation_match.group(2)
                # for now we don't use this since my model is too basic
                # aggregation = aggregation_match.group(1)
                this_value = {clean_record_key(name): value}

            else:
                this_value = {clean_record_key(key): value}

            if this_dimension:
                all_dimensions.add(this_dimension)
            elif this_value:
                all_values.update(this_value)

        if measure_flag:
            all_values[clean_record_key(measure_name)] = measure_value

        all_dimensions = Dimensions(frozenset(all_dimensions))

        if all_dimensions in marks:
            marks[all_dimensions].values_dict.update(all_values)

        else:
            new_mark = Mark(all_dimensions)
            new_mark.values_dict = all_values
            marks[all_dimensions] = new_mark

    return list(marks.values())
