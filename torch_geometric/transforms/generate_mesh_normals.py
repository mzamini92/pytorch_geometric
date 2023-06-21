import torch
import torch.nn.functional as F

from torch_geometric.data import Data
from torch_geometric.data.datapipes import functional_transform
from torch_geometric.transforms import BaseTransform
from torch_geometric.utils import scatter


@functional_transform('generate_mesh_normals')
class GenerateMeshNormals(BaseTransform):
    r"""Generate normal vectors for each mesh node based on neighboring
    faces (functional name: :obj:`generate_mesh_normals`)."""
    def forward(self, data: Data) -> Data:
        assert 'face' in data
        pos, face = data.pos, data.face

        # Calculate face normals
        vec1 = pos[face[:, 1]] - pos[face[:, 0]]
        vec2 = pos[face[:, 2]] - pos[face[:, 0]]
        face_norm = F.normalize(vec1.cross(vec2), p=2,
                                dim=-1)  # [num_faces, 3]

        # Assign face normals to vertices
        idx = face.view(-1)
        norm = scatter(face_norm.repeat(3, 1), idx, 0, pos.size(0),
                       reduce='sum')
        norm = F.normalize(norm, p=2, dim=-1)  # [num_nodes, 3]

        data.norm = norm

        return data
